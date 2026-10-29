"""MediaPipe model manager and vision task pipeline for GhostCam Studio."""

from __future__ import annotations

import os
import shutil
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

from .config import (
    FACE_MODEL_PATH,
    HAND_MODEL_PATH,
    MODEL_DOWNLOAD_URLS,
    MODELS_DIR,
    SEGMENTER_MODEL_PATH,
)


def ensure_models_available() -> None:
    """Ensure required MediaPipe task models are present in models/."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    # Check if a sibling repository already has downloaded models to avoid redundant downloads
    sibling_dir = Path(r"c:\repos\vanish_webcam")
    sibling_candidates = {
        SEGMENTER_MODEL_PATH: sibling_dir / "models" / "selfie_segmenter_landscape.tflite",
        HAND_MODEL_PATH: sibling_dir / "hand_landmarker.task",
        FACE_MODEL_PATH: sibling_dir / "face_landmarker.task",
    }

    for target_path, url in MODEL_DOWNLOAD_URLS.items():
        if target_path.is_file() and target_path.stat().st_size > 100_000:
            continue
        sibling = sibling_candidates.get(target_path)
        if sibling is not None and sibling.is_file() and sibling.stat().st_size > 100_000:
            shutil.copy2(sibling, target_path)
            continue

        temp_path = target_path.with_suffix(target_path.suffix + ".tmp")
        print(f"[GhostCam] Downloading model {target_path.name}...")
        req = urllib.request.Request(url, headers={"User-Agent": "GhostCam-Studio/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp, temp_path.open("wb") as out:
                shutil.copyfileobj(resp, out)
            os.replace(temp_path, target_path)
        except Exception as exc:
            temp_path.unlink(missing_ok=True)
            raise RuntimeError(f"Failed to download {target_path.name}: {exc}") from exc


class VisionPipeline:
    """Unified MediaPipe segmentation + hand & face landmark tracker."""

    def __init__(self, need_face: bool = True) -> None:
        ensure_models_available()
        seg_opts = mp_vision.ImageSegmenterOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(SEGMENTER_MODEL_PATH)),
            running_mode=mp_vision.RunningMode.VIDEO,
            output_confidence_masks=True,
            output_category_mask=False,
        )
        hand_opts = mp_vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(HAND_MODEL_PATH)),
            running_mode=mp_vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.35,
            min_hand_presence_confidence=0.35,
            min_tracking_confidence=0.45,
        )
        self.segmenter = mp_vision.ImageSegmenter.create_from_options(seg_opts)
        self.hand_detector = mp_vision.HandLandmarker.create_from_options(hand_opts)
        self.face_detector = None
        if need_face:
            face_opts = mp_vision.FaceLandmarkerOptions(
                base_options=mp_python.BaseOptions(model_asset_path=str(FACE_MODEL_PATH)),
                running_mode=mp_vision.RunningMode.VIDEO,
                num_faces=1,
                min_face_detection_confidence=0.35,
                min_face_presence_confidence=0.35,
                min_tracking_confidence=0.45,
            )
            self.face_detector = mp_vision.FaceLandmarker.create_from_options(face_opts)

        self._cached_face = []
        self._cached_face_ms = -10_000

    def segment_person(self, mp_image: mp.Image, timestamp_ms: int, width: int, height: int) -> np.ndarray:
        result = self.segmenter.segment_for_video(mp_image, timestamp_ms)
        if not result.confidence_masks:
            return np.zeros((height, width), dtype=np.float32)
        raw = np.squeeze(result.confidence_masks[0].numpy_view()).astype(np.float32)
        resized = cv2.resize(raw, (width, height), interpolation=cv2.INTER_LINEAR)
        blurred = cv2.GaussianBlur(resized, (0, 0), sigmaX=2.0, sigmaY=2.0)
        return np.clip((blurred - 0.14) / 0.68, 0.0, 1.0)

    def detect_landmarks(self, mp_image: mp.Image, timestamp_ms: int) -> tuple[list, list]:
        hand_res = self.hand_detector.detect_for_video(mp_image, timestamp_ms)
        hands = hand_res.hand_landmarks
        faces = []
        if self.face_detector is not None:
            face_res = self.face_detector.detect_for_video(mp_image, timestamp_ms)
            if face_res.face_landmarks:
                self._cached_face = face_res.face_landmarks
                self._cached_face_ms = timestamp_ms
                faces = face_res.face_landmarks
            elif self._cached_face and (timestamp_ms - self._cached_face_ms) <= 2500:
                faces = self._cached_face
        return hands, faces

    def close(self) -> None:
        for task in (self.segmenter, self.hand_detector, self.face_detector):
            if task is not None:
                try:
                    task.close()
                except Exception:
                    pass
