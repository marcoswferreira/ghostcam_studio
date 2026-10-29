"""Mode 1: Normal Vanish (Dissolve) — organic multi-octave wave dissolve with glowing plasma edge."""

from __future__ import annotations

import cv2
import numpy as np


class NormalDissolveEffect:
    """Smooth top-to-bottom organic dissolve with a shimmering cyan-gold plasma frontier."""

    duration = 3.60

    def __init__(self) -> None:
        self._field: np.ndarray | None = None
        self._sparkle: np.ndarray | None = None

    def _build_fields(self, height: int, width: int) -> None:
        if self._field is not None and self._field.shape == (height, width):
            return
        rng = np.random.default_rng(7391)
        y_grid, x_grid = np.mgrid[0:height, 0:width].astype(np.float32)
        y_norm = y_grid / max(1, height - 1)
        x_norm = x_grid / max(1, width - 1)

        coarse = rng.random((max(2, height // 10), max(2, width // 10)), dtype=np.float32)
        coarse_up = cv2.resize(coarse, (width, height), interpolation=cv2.INTER_CUBIC)
        fine = rng.random((height, width), dtype=np.float32)

        field = (1.0 - y_norm) * 0.72 + coarse_up * 0.17 + fine * 0.08 + np.sin(x_norm * 18.0) * 0.025
        self._field = np.clip(field, 0.0, 1.0)
        self._sparkle = fine

    def reset(self, frame: np.ndarray, mask: np.ndarray) -> None:
        h, w = frame.shape[:2]
        self._build_fields(h, w)

    def render(
        self,
        frame: np.ndarray,
        background: np.ndarray,
        mask: np.ndarray,
        age: float,
        reverse: bool = False,
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        self._build_fields(h, w)

        progress = float(np.clip(age / self.duration, 0.0, 1.0))
        if reverse:
            progress = 1.0 - progress

        if progress <= 0.002:
            a3 = mask[:, :, None]
            return (frame.astype(np.float32) * a3 + background.astype(np.float32) * (1.0 - a3)).astype(np.uint8)
        if progress >= 0.999:
            return background.copy()

        pts = cv2.findNonZero((mask > 0.01).astype(np.uint8))
        if pts is None:
            return background.copy()

        bx, by, bw, bh = cv2.boundingRect(pts)
        left, top = max(0, bx - 18), max(0, by - 18)
        right, bot = min(w, bx + bw + 18), min(h, by + bh + 18)
        roi = np.s_[top:bot, left:right]

        sub_mask = mask[roi]
        sub_field = self._field[roi]
        sub_sparkle = self._sparkle[roi]

        # Cubic ease-in-out
        eased = (
            4.0 * (progress ** 3)
            if progress < 0.5
            else 1.0 - ((-2.0 * progress + 2.0) ** 3) * 0.5
        )
        t_val = np.clip((sub_field - (eased - 0.055)) / 0.11, 0.0, 1.0)
        survival = t_val * t_val * (3.0 - 2.0 * t_val)
        alpha = (sub_mask * survival)[:, :, None]

        blended = (
            frame[roi].astype(np.float32) * alpha
            + background[roi].astype(np.float32) * (1.0 - alpha)
        ).astype(np.uint8)

        edge = ((np.abs(sub_field - eased) < 0.018) & (sub_mask > 0.48) & (sub_sparkle > 0.54)).astype(np.float32)
        glow = cv2.GaussianBlur(edge, (0, 0), sigmaX=5.0, sigmaY=5.0)
        glow = np.clip(glow * 5.0 + edge, 0.0, 1.0)[:, :, None]
        rim_color = np.full_like(blended, (255, 228, 92), dtype=np.uint8)
        roi_out = np.clip(
            blended.astype(np.float32) * (1.0 - glow * 0.8) + rim_color.astype(np.float32) * (glow * 0.8),
            0,
            255,
        ).astype(np.uint8)

        canvas = background.copy()
        canvas[roi] = roi_out
        return canvas

    def render_vanished(
        self, frame: np.ndarray, background: np.ndarray, mask: np.ndarray, age: float
    ) -> np.ndarray:
        return background.copy()
