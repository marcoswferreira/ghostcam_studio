"""Command-line entrypoint for GhostCam Studio."""

from __future__ import annotations

import argparse
import sys

from ghostcam.audio import SoundBank, ensure_synthesized_sounds
from ghostcam.config import EFFECT_BY_KEY, EFFECT_CATALOG, StudioConfig
from ghostcam.effects import create_effect
from ghostcam.engine import run_studio
from ghostcam.models import VisionPipeline, ensure_models_available
from ghostcam.ui import select_effect_dialog


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="GhostCam Studio — Real-Time Webcam Disappearance & VFX Engine."
    )
    parser.add_argument("--camera", type=int, default=0, help="Physical webcam index (default: 0)")
    parser.add_argument("--width", type=int, default=960, help="Video width (default: 960)")
    parser.add_argument("--height", type=int, default=540, help="Video height (default: 540)")
    parser.add_argument("--fps", type=float, default=30.0, help="Target frame rate (default: 30)")
    parser.add_argument("--no-mirror", action="store_true", help="Disable horizontal webcam mirroring")
    parser.add_argument("--fullscreen", action="store_true", help="Start preview window in fullscreen")
    parser.add_argument(
        "--mode",
        choices=tuple(EFFECT_BY_KEY.keys()),
        help="Skip launcher menu and start directly in the chosen effect mode",
    )
    parser.add_argument(
        "--virtual-camera",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Require virtual camera output (--no-virtual-camera disables it)",
    )
    parser.add_argument(
        "--virtual-backend",
        choices=("obs", "unitycapture", "v4l2loopback"),
        help="Virtual camera backend driver",
    )
    parser.add_argument("--virtual-device", help="Virtual camera device name")
    parser.add_argument("--gesture-debug", action="store_true", help="Print gesture detection diagnostics")
    parser.add_argument("--self-test", action="store_true", help="Run automated self-test of models, sounds, and effects")
    return parser.parse_args()


def run_self_test() -> int:
    ensure_models_available()
    paths = ensure_synthesized_sounds()
    for name, path in paths.items():
        if not path.is_file():
            raise RuntimeError(f"Missing synthesized sound for {name}: {path}")
    bank = SoundBank()
    bank.close()
    vision = VisionPipeline(need_face=True)
    vision.close()
    for key in EFFECT_BY_KEY:
        create_effect(key)
    print(
        f"[GhostCam] Self-test passed: all {len(EFFECT_CATALOG)} catalog effects "
        "(including Goku & Naruto), MediaPipe models, and synthesized sounds verified."
    )
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    chosen_mode = args.mode or select_effect_dialog()
    if chosen_mode is None:
        return 0

    cfg = StudioConfig(
        camera_index=args.camera,
        width=args.width,
        height=args.height,
        fps=args.fps,
        mirror=not args.no_mirror,
        fullscreen=args.fullscreen,
        mode=chosen_mode,
        virtual_camera=args.virtual_camera,
        virtual_backend=args.virtual_backend,
        virtual_device=args.virtual_device,
        debug_gestures=args.gesture_debug,
    )
    try:
        return run_studio(cfg, chosen_mode)
    except KeyboardInterrupt:
        return 0
    except Exception as exc:
        print(f"\n[GhostCam] ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
