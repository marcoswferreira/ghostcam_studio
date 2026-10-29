"""Real-time video processing loop and virtual camera broadcaster for GhostCam Studio."""

from __future__ import annotations

from contextlib import ExitStack
import platform
import time

import cv2
import mediapipe as mp
import numpy as np

from .audio import SoundBank
from .config import EFFECT_BY_KEY, EFFECT_CATALOG, StudioConfig
from .effects import create_effect
from .effects.goku import GOKU_HOLD_SECONDS
from .gestures import detect_mode_gesture
from .models import VisionPipeline


PREVIEW_WINDOW_TITLE = "GhostCam Studio - Live Feed"


def open_physical_camera(index: int, width: int, height: int, fps: float) -> cv2.VideoCapture:
    if platform.system() == "Windows":
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap.release()
            cap = cv2.VideoCapture(index)
    else:
        cap = cv2.VideoCapture(index)

    if not cap.isOpened():
        raise RuntimeError(f"Camera {index} is unavailable. Close other apps using it or pass --camera 1.")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def open_virtual_output(config: StudioConfig, width: int, height: int):
    if config.virtual_camera is False:
        return None
    try:
        import pyvirtualcam

        vcam = pyvirtualcam.Camera(
            width=width,
            height=height,
            fps=config.fps,
            fmt=pyvirtualcam.PixelFormat.BGR,
            backend=config.virtual_backend,
            device=config.virtual_device,
        )
        print(f"[GhostCam] Virtual Camera active: {vcam.device} ({width}x{height} @ {config.fps:g} FPS)")
        return vcam
    except Exception as exc:
        msg = (
            "Virtual camera driver not available. Install OBS Studio (for OBS Virtual Camera) "
            f"or Unity Capture. Detail: {exc}"
        )
        if config.virtual_camera is True or config.virtual_backend or config.virtual_device:
            raise RuntimeError(msg) from exc
        print(f"[GhostCam] {msg}\n[GhostCam] Continuing with local preview window.")
        return None


def run_studio(config: StudioConfig, initial_mode: str) -> int:
    active_mode = initial_mode
    effect = create_effect(active_mode)
    max_num = len(EFFECT_CATALOG)

    with ExitStack() as stack:
        vision = VisionPipeline(need_face=True)
        stack.callback(vision.close)

        sounds = SoundBank()
        stack.callback(sounds.close)

        cap = open_physical_camera(config.camera_index, config.width, config.height, config.fps)
        stack.callback(cap.release)

        stack.callback(cv2.destroyAllWindows)
        cv2.namedWindow(PREVIEW_WINDOW_TITLE, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(PREVIEW_WINDOW_TITLE, config.width, config.height)

        vcam = None
        vcam_opened = False

        phase = "calibrating"
        started_at = time.perf_counter()
        calibration_start = started_at
        effect_start: float | None = None
        last_gesture_check = 0.0
        last_mask_time = -10.0
        last_mask: np.ndarray | None = None
        bg_samples: list[np.ndarray] = []
        background: np.ndarray | None = None
        countdown_printed: int | None = None
        hold_started: float | None = None
        goku_countdown_reported: int | None = None
        gesture_rearmed = True

        spec = EFFECT_BY_KEY[active_mode]
        print(f"[GhostCam] Active Mode: {spec.title} — {spec.gesture_hint}")
        print(f"[GhostCam] Step out of the camera frame for {config.calibration_seconds:.0f}s to capture the empty background.")
        print(
            f"[GhostCam] Controls: [1-{max_num}] Switch Effect | [SPACE] Recapture Background | "
            "[V] Vanish | [R] Reappear | [F] Fullscreen | [Q] Quit"
        )

        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                raise RuntimeError("Webcam stopped sending frames.")

            if config.mirror:
                frame = cv2.flip(frame, 1)

            h, w = frame.shape[:2]
            if not vcam_opened:
                vcam = open_virtual_output(config, w, h)
                vcam_opened = True
                if vcam is not None:
                    stack.callback(vcam.close)

            now = time.perf_counter()
            ts_ms = int((now - started_at) * 1000)
            mp_img: mp.Image | None = None

            if phase == "calibrating":
                elapsed = now - calibration_start
                rem = max(0, int(np.ceil(config.calibration_seconds - elapsed)))
                if rem != countdown_printed:
                    print(f"[GhostCam] Capturing background: {rem}s remaining...")
                    countdown_printed = rem
                if elapsed >= config.calibration_seconds - 0.65:
                    bg_samples.append(frame.copy())
                if elapsed >= config.calibration_seconds:
                    if bg_samples:
                        background = np.median(np.stack(bg_samples[-16:], axis=0), axis=0).astype(np.uint8)
                    else:
                        background = frame.copy()
                    bg_samples.clear()
                    phase = "ready"
                    hold_started = None
                    goku_countdown_reported = None
                    gesture_rearmed = True
                    print("[GhostCam] Background ready! Step back into the camera frame.")
                output = frame

            elif background is None:
                phase = "calibrating"
                calibration_start = now
                output = frame

            else:
                # Check hand/face gestures in 'ready' phase, or also in 'vanished' phase for goku/teleport/stealth
                can_detect = phase == "ready" or (
                    phase == "vanished" and active_mode in ("goku", "teleport", "stealth")
                )
                if can_detect and (now - last_gesture_check) >= 0.08:
                    last_gesture_check = now
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                    hands, faces = vision.detect_landmarks(mp_img, ts_ms)
                    matched = detect_mode_gesture(active_mode, hands, faces, w, h)

                    if config.debug_gestures:
                        print(f"[Debug] mode={active_mode} hands={len(hands)} faces={len(faces)} matched={matched}")

                    is_goku_mode = active_mode in ("goku", "teleport")
                    if not matched:
                        if is_goku_mode and hold_started is not None:
                            print("[Goku] Pose interrupted: countdown reset.")
                        hold_started = None
                        goku_countdown_reported = None
                        gesture_rearmed = True
                    elif gesture_rearmed:
                        req_hold = GOKU_HOLD_SECONDS if is_goku_mode else 0.0
                        if hold_started is None:
                            hold_started = now
                            goku_countdown_reported = None
                        held = now - hold_started
                        if is_goku_mode:
                            tenths_left = max(0, int(np.ceil((req_hold - held) * 10)))
                            if tenths_left != goku_countdown_reported and tenths_left in (10, 7, 4, 1):
                                print(f"[Goku] Teleporting in {tenths_left / 10:.1f}s...")
                                goku_countdown_reported = tenths_left
                        if held >= req_hold:
                            hold_started = None
                            goku_countdown_reported = None
                            gesture_rearmed = False
                            if mp_img is None:
                                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                            last_mask = vision.segment_person(mp_img, ts_ms, w, h)
                            last_mask_time = now
                            effect.reset(frame, last_mask)
                            effect_start = time.perf_counter()
                            sounds.play(active_mode)
                            if phase == "vanished":
                                phase = "returning"
                                if is_goku_mode:
                                    print("[Goku] Instant Transmission return!")
                                else:
                                    print(f"[GhostCam] Triggered {active_mode} (returning)!")
                            else:
                                phase = "vanishing"
                                if is_goku_mode:
                                    print("[Goku] Instant Transmission!")
                                else:
                                    print(f"[GhostCam] Triggered {active_mode} (vanishing)!")

                # Update person segmentation mask when needed
                need_live_mask = (
                    phase in ("vanishing", "returning")
                    and active_mode not in ("particles", "disintegration")
                    and (last_mask is None or (now - last_mask_time) >= 0.05)
                ) or (phase == "vanished" and active_mode == "stealth" and (now - last_mask_time) >= 0.06)

                if need_live_mask:
                    if mp_img is None:
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                    last_mask = vision.segment_person(mp_img, ts_ms, w, h)
                    last_mask_time = now

                mask_to_use = last_mask if last_mask is not None else np.zeros((h, w), dtype=np.float32)

                if phase == "ready":
                    output = frame
                elif phase in ("vanishing", "returning"):
                    age = max(0.0, time.perf_counter() - (effect_start or now))
                    is_rev = phase == "returning"
                    output = effect.render(frame, background, mask_to_use, age, reverse=is_rev)
                    if age >= effect.duration:
                        phase = "ready" if is_rev else "vanished"
                        effect_start = time.perf_counter()
                else:
                    age = max(0.0, time.perf_counter() - (effect_start or now))
                    output = effect.render_vanished(frame, background, mask_to_use, age)

            if vcam is not None:
                if output.shape[:2] != (vcam.height, vcam.width):
                    vcam_frame = cv2.resize(output, (vcam.width, vcam.height), interpolation=cv2.INTER_LINEAR)
                else:
                    vcam_frame = output
                vcam.send(np.ascontiguousarray(vcam_frame))

            cv2.imshow(PREVIEW_WINDOW_TITLE, output)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord(" "):
                phase = "calibrating"
                calibration_start = now
                countdown_printed = None
                hold_started = None
                goku_countdown_reported = None
                gesture_rearmed = True
                bg_samples.clear()
                print(f"[GhostCam] Step out of the frame for {config.calibration_seconds:.0f}s: capturing new background...")
            elif key == ord("v") and background is not None:
                if mp_img is None:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                last_mask = vision.segment_person(mp_img, ts_ms, w, h)
                last_mask_time = now
                effect.reset(frame, last_mask)
                effect_start = time.perf_counter()
                sounds.play(active_mode)
                phase = "vanishing"
            elif key == ord("r") and background is not None:
                if active_mode in ("goku", "teleport", "stealth", "portal") and phase == "vanished":
                    effect_start = time.perf_counter()
                    sounds.play(active_mode)
                    phase = "returning"
                else:
                    phase = "ready"
            elif key == ord("f"):
                config.fullscreen = not config.fullscreen
                prop = cv2.WINDOW_FULLSCREEN if config.fullscreen else cv2.WINDOW_NORMAL
                cv2.setWindowProperty(PREVIEW_WINDOW_TITLE, cv2.WND_PROP_FULLSCREEN, prop)
            else:
                for item in EFFECT_CATALOG:
                    if key == ord(str(item.number)):
                        active_mode = item.key
                        effect = create_effect(active_mode)
                        phase = "ready"
                        hold_started = None
                        goku_countdown_reported = None
                        gesture_rearmed = True
                        print(f"[GhostCam] Switched to {item.title} — {item.gesture_hint}")
                        break

            if vcam is not None:
                vcam.sleep_until_next_frame()

    return 0
