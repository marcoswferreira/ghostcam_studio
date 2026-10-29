"""Procedural stereo sound effect synthesizer and non-blocking audio player."""

from __future__ import annotations

import os
import wave
from pathlib import Path

import numpy as np

from .config import SOUNDS_DIR


SAMPLE_RATE = 44100


def _write_stereo_wav(path: Path, left: np.ndarray, right: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = max(1e-6, float(np.max(np.abs([left, right]))))
    l_pcm = np.int16(np.clip(left / peak * 0.88, -1.0, 1.0) * 32767)
    r_pcm = np.int16(np.clip(right / peak * 0.88, -1.0, 1.0) * 32767)
    stereo = np.column_stack((l_pcm, r_pcm))
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(stereo.tobytes())


def ensure_synthesized_sounds() -> dict[str, Path]:
    """Generate procedural stereo sound effects for all 5 modes if not already cached."""
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    paths = {
        "teleport": SOUNDS_DIR / "teleport.wav",
        "disintegration": SOUNDS_DIR / "disintegration.wav",
        "smoke": SOUNDS_DIR / "smoke.wav",
        "stealth": SOUNDS_DIR / "stealth.wav",
        "portal": SOUNDS_DIR / "portal.wav",
    }

    if not paths["teleport"].is_file():
        t = np.linspace(0, 0.50, int(SAMPLE_RATE * 0.50), endpoint=False)
        freq = 1680 + 920 * np.sin(2 * np.pi * 66 * t) + 650 * (t / 0.50) ** 2
        phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
        env = np.exp(-3.9 * t) * np.minimum(1.0, t / 0.008)
        snap = np.where(t > 0.13, np.exp(-9.5 * np.maximum(0, t - 0.13)) * np.sin(2 * np.pi * 2900 * t), 0.0)
        sig = (np.sin(phase) + 0.45 * np.sin(phase * 0.5) + 0.25 * np.sin(phase * 1.5)) * env + 0.4 * snap
        _write_stereo_wav(paths["teleport"], sig, np.roll(sig, 18))

    if not paths["disintegration"].is_file():
        t = np.linspace(0, 1.35, int(SAMPLE_RATE * 1.35), endpoint=False)
        rng = np.random.default_rng(1042)
        noise = rng.normal(0, 1, len(t))
        # Shimmering crystalline wind chime + airy sweep
        chime = (
            np.sin(2 * np.pi * 880 * t) * np.exp(-2.8 * t)
            + 0.6 * np.sin(2 * np.pi * 1320 * t) * np.exp(-2.2 * t)
            + 0.4 * np.sin(2 * np.pi * 1760 * t) * np.exp(-1.8 * t)
        )
        wind_env = np.sin(np.pi * (t / 1.35)) ** 1.4
        sig_l = 0.55 * chime + 0.35 * noise * wind_env
        sig_r = 0.55 * chime + 0.35 * np.roll(noise, 60) * wind_env
        _write_stereo_wav(paths["disintegration"], sig_l, sig_r)

    if not paths["smoke"].is_file():
        t = np.linspace(0, 0.65, int(SAMPLE_RATE * 0.65), endpoint=False)
        rng = np.random.default_rng(2084)
        burst = rng.normal(0, 1, len(t)) * np.exp(-6.5 * t) * np.minimum(1.0, t / 0.005)
        thump = np.sin(2 * np.pi * (160 * np.exp(-7.0 * t) + 45) * t) * np.exp(-5.0 * t)
        sig = 0.75 * thump + 0.55 * burst
        _write_stereo_wav(paths["smoke"], sig, sig)

    if not paths["stealth"].is_file():
        t = np.linspace(0, 0.72, int(SAMPLE_RATE * 0.72), endpoint=False)
        sweep = 320 + 1400 * (t / 0.72) ** 1.7
        phase = 2 * np.pi * np.cumsum(sweep) / SAMPLE_RATE
        mod = 0.5 + 0.5 * np.sin(2 * np.pi * 28 * t)
        env = np.sin(np.pi * (t / 0.72))
        sig = np.sin(phase) * mod * env
        _write_stereo_wav(paths["stealth"], sig, -sig)

    if not paths["portal"].is_file():
        t = np.linspace(0, 1.25, int(SAMPLE_RATE * 1.25), endpoint=False)
        vortex_freq = 110 + 240 * np.sin(np.pi * t / 1.25) + 35 * np.sin(2 * np.pi * 9 * t)
        phase = 2 * np.pi * np.cumsum(vortex_freq) / SAMPLE_RATE
        env = np.sin(np.pi * (t / 1.25)) ** 0.8
        sig_l = (np.sin(phase) + 0.5 * np.sin(phase * 2.02)) * env
        sig_r = (np.sin(phase + 0.6) + 0.5 * np.sin(phase * 1.98)) * env
        _write_stereo_wav(paths["portal"], sig_l, sig_r)

    return paths


class SoundBank:
    """Non-blocking sound effect player backed by pygame.mixer."""

    def __init__(self) -> None:
        os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
        self.paths = ensure_synthesized_sounds()
        self.sounds: dict[str, object] = {}
        self.mixer = None
        self.owns_mixer = False
        try:
            from pygame import mixer

            self.mixer = mixer
            self.owns_mixer = mixer.get_init() is None
            if self.owns_mixer:
                mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=256)
            for key, path in self.paths.items():
                self.sounds[key] = mixer.Sound(str(path))
        except Exception:
            self.mixer = None

    def play(self, effect_key: str) -> None:
        sound = self.sounds.get(effect_key)
        if sound is not None:
            try:
                sound.stop()
                sound.play()
            except Exception:
                pass

    def close(self) -> None:
        if self.mixer is not None and self.owns_mixer:
            try:
                self.mixer.quit()
            except Exception:
                pass
            self.owns_mixer = False
