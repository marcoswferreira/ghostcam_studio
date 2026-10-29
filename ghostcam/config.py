"""Configuration and constants for GhostCam Studio."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT_DIR / "models"
SOUNDS_DIR = ROOT_DIR / "assets" / "generated_sounds"

SEGMENTER_MODEL_PATH = MODELS_DIR / "selfie_segmenter_landscape.tflite"
HAND_MODEL_PATH = MODELS_DIR / "hand_landmarker.task"
FACE_MODEL_PATH = MODELS_DIR / "face_landmarker.task"

MODEL_DOWNLOAD_URLS = {
    SEGMENTER_MODEL_PATH: (
        "https://storage.googleapis.com/mediapipe-models/image_segmenter/"
        "selfie_segmenter_landscape/float16/latest/selfie_segmenter_landscape.tflite"
    ),
    HAND_MODEL_PATH: (
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
        "hand_landmarker/float16/1/hand_landmarker.task"
    ),
    FACE_MODEL_PATH: (
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
        "face_landmarker/float16/1/face_landmarker.task"
    ),
}


@dataclass(frozen=True)
class EffectSpec:
    key: str
    number: int
    title: str
    subtitle: str
    gesture_hint: str
    duration: float
    persistent_vanish: bool = True


EFFECT_CATALOG: tuple[EffectSpec, ...] = (
    EffectSpec(
        key="teleport",
        number=1,
        title="1  INSTANT TELEPORT",
        subtitle="Anime Speed Lines & Instant Transmission",
        gesture_hint="Hold index + middle fingers on forehead (1.0s) to vanish & return",
        duration=0.52,
        persistent_vanish=True,
    ),
    EffectSpec(
        key="disintegration",
        number=2,
        title="2  COSMIC DISINTEGRATION",
        subtitle="Particle Shatter & Wind Dispersion",
        gesture_hint="Make a V-sign (peace gesture) with index + middle fingers",
        duration=2.15,
        persistent_vanish=True,
    ),
    EffectSpec(
        key="smoke",
        number=3,
        title="3  NINJA SMOKE BOMB",
        subtitle="Smoke Cloud & Decoy Substitution",
        gesture_hint="Bring both open palms together in front of your chest",
        duration=1.45,
        persistent_vanish=True,
    ),
    EffectSpec(
        key="stealth",
        number=4,
        title="4  OPTICAL STEALTH CLOAK",
        subtitle="Predator / Cyberpunk Refraction Camouflage",
        gesture_hint="Raise an open palm (5 fingers spread) to toggle active camo",
        duration=1.10,
        persistent_vanish=True,
    ),
    EffectSpec(
        key="portal",
        number=5,
        title="5  DIMENSIONAL PORTAL",
        subtitle="Swirling Energy Vortex & Gravitational Pull",
        gesture_hint="Make a Rock-On / Horns gesture (index + pinky extended)",
        duration=1.95,
        persistent_vanish=True,
    ),
)

EFFECT_BY_KEY = {spec.key: spec for spec in EFFECT_CATALOG}


@dataclass
class StudioConfig:
    camera_index: int = 0
    width: int = 960
    height: int = 540
    fps: float = 30.0
    mirror: bool = True
    fullscreen: bool = False
    mode: str | None = None
    virtual_camera: bool | None = None
    virtual_backend: str | None = None
    virtual_device: str | None = None
    calibration_seconds: float = 4.0
    debug_gestures: bool = False
