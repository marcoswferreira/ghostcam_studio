"""Mode 4: Optical Stealth Cloak — Predator/Cyberpunk active refraction camouflage."""

from __future__ import annotations

import cv2
import numpy as np


class StealthCloakEffect:
    duration = 1.10

    def reset(self, frame: np.ndarray, mask: np.ndarray) -> None:
        pass

    def _apply_refraction(
        self,
        frame: np.ndarray,
        background: np.ndarray,
        mask: np.ndarray,
        cloak_amount: float,
        time_sec: float,
    ) -> np.ndarray:
        """Blend person into a shimmering glass-refracted background with neon scanline edge."""
        height, width = background.shape[:2]
        y_grid, x_grid = np.mgrid[0:height, 0:width].astype(np.float32)

        # Compute normal/gradient of silhouette mask for lens-like edge bending
        gx = cv2.Sobel(mask, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(mask, cv2.CV_32F, 0, 1, ksize=3)
        ripple = np.sin(y_grid * 0.18 - time_sec * 9.0) * 4.5 + np.cos(x_grid * 0.14 + time_sec * 6.0) * 3.5

        strength = cloak_amount * 14.0
        map_x = np.clip(x_grid + (gx * 22.0 + ripple * 0.35) * mask * (strength / 14.0), 0, width - 1)
        map_y = np.clip(y_grid + (gy * 22.0 + ripple * 0.25) * mask * (strength / 14.0), 0, height - 1)
        refracted_bg = cv2.remap(background, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        # Blend live person with refracted background based on cloak_amount
        person_visibility = (1.0 - cloak_amount * 0.94) * mask
        cloaked = (
            frame.astype(np.float32) * person_visibility[:, :, None]
            + refracted_bg.astype(np.float32) * (1.0 - person_visibility[:, :, None])
        ).astype(np.uint8)

        # Neon holographic rim at the silhouette boundary + transition wave
        edge = np.hypot(gx, gy)
        rim = np.clip(edge * 1.8, 0.0, 1.0)
        scan_wave = 0.5 + 0.5 * np.sin(y_grid * 0.25 - time_sec * 14.0)
        glow_intensity = rim * (0.35 + 0.65 * (1.0 - abs(2.0 * cloak_amount - 1.0))) * scan_wave
        cyan_neon = np.array([255, 235, 70], dtype=np.float32)
        cloaked = np.clip(
            cloaked.astype(np.float32) * (1.0 - glow_intensity[:, :, None] * 0.75)
            + cyan_neon * (glow_intensity[:, :, None] * 0.75),
            0,
            255,
        ).astype(np.uint8)
        return cloaked

    def render(
        self,
        frame: np.ndarray,
        background: np.ndarray,
        mask: np.ndarray,
        age: float,
        reverse: bool = False,
    ) -> np.ndarray:
        progress = float(np.clip(age / self.duration, 0.0, 1.0))
        if reverse:
            progress = 1.0 - progress
        return self._apply_refraction(frame, background, mask, cloak_amount=progress, time_sec=age)

    def render_vanished(self, frame: np.ndarray, background: np.ndarray, mask: np.ndarray, age: float) -> np.ndarray:
        # While vanished in Stealth mode, keep a subtle Predator shimmer where the user moves!
        return self._apply_refraction(frame, background, mask, cloak_amount=1.0, time_sec=age)

