"""Mode 5: Dimensional Portal — swirling energy vortex and gravitational spiral pull."""

from __future__ import annotations

import math

import cv2
import numpy as np


class DimensionalPortalEffect:
    duration = 1.95

    def __init__(self) -> None:
        self.center: tuple[int, int] = (320, 240)
        self.max_radius: float = 160.0

    def reset(self, frame: np.ndarray, mask: np.ndarray) -> None:
        h, w = mask.shape[:2]
        pts = cv2.findNonZero((mask > 0.35).astype(np.uint8))
        if pts is None:
            self.center = (w // 2, h // 2)
            self.max_radius = min(w, h) * 0.38
            return
        bx, by, bw, bh = cv2.boundingRect(pts)
        self.center = (int(bx + bw * 0.5), int(by + bh * 0.48))
        self.max_radius = float(max(bw, bh) * 0.56)

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

        height, width = frame.shape[:2]
        cx, cy = self.center

        # Portal radius grows open (0..0.25), stays open (0.25..0.75), then snaps shut (0.75..1.0)
        if progress < 0.25:
            portal_scale = progress / 0.25
        elif progress < 0.75:
            portal_scale = 1.0
        else:
            portal_scale = max(0.0, 1.0 - (progress - 0.75) / 0.25)

        radius = max(4.0, self.max_radius * portal_scale)
        output = background.copy()

        # Draw swirling portal vortex behind the user
        y_grid, x_grid = np.mgrid[0:height, 0:width].astype(np.float32)
        dx = x_grid - cx
        dy = (y_grid - cy) * 1.18  # Slightly elliptical vertical portal
        dist = np.hypot(dx, dy)
        angle = np.arctan2(dy, dx)

        inside_portal = dist < radius
        if np.any(inside_portal):
            norm_r = dist / max(1.0, radius)
            swirl_angle = angle + (1.0 - norm_r) * 7.5 - age * 9.0
            spiral_pattern = 0.5 + 0.5 * np.sin(swirl_angle * 4.0 + norm_r * 12.0)

            # Deep cosmic violet interior with bright orange/gold energy ring
            vortex_b = np.clip(180 * (1.0 - norm_r * 0.5) + 75 * spiral_pattern, 0, 255)
            vortex_g = np.clip(45 * (1.0 - norm_r) + 165 * (norm_r ** 2) * spiral_pattern, 0, 255)
            vortex_r = np.clip(95 * (1.0 - norm_r) + 255 * norm_r * spiral_pattern, 0, 255)
            vortex = np.stack([vortex_b, vortex_g, vortex_r], axis=-1).astype(np.float32)

            rim_glow = np.exp(-((norm_r - 0.88) ** 2) / 0.012)
            vortex += np.array([40, 190, 255], dtype=np.float32) * rim_glow[:, :, None]
            vortex = np.clip(vortex, 0, 255)

            portal_alpha = np.clip((1.0 - (norm_r ** 4)) * min(1.0, portal_scale * 1.4), 0.0, 1.0)[:, :, None]
            output = (vortex * portal_alpha + output.astype(np.float32) * (1.0 - portal_alpha)).astype(np.uint8)

        # Pull person silhouette into the portal center with spiral twist
        if progress < 0.78:
            pull_t = min(1.0, max(0.0, (progress - 0.10) / 0.68))
            scale_inv = 1.0 / max(0.08, 1.0 - 0.92 * (pull_t ** 1.6))
            twist = pull_t * 2.6 * np.exp(-dist / max(20.0, self.max_radius * 1.2))
            cos_t = np.cos(twist)
            sin_t = np.sin(twist)
            raw_dx = x_grid - cx
            raw_dy = y_grid - cy
            src_x = cx + (raw_dx * cos_t - raw_dy * sin_t) * scale_inv
            src_y = cy + (raw_dx * sin_t + raw_dy * cos_t) * scale_inv

            warped_person = cv2.remap(frame, src_x.astype(np.float32), src_y.astype(np.float32), cv2.INTER_LINEAR)
            warped_mask = cv2.remap(mask, src_x.astype(np.float32), src_y.astype(np.float32), cv2.INTER_LINEAR)
            person_alpha = (warped_mask * (1.0 - pull_t ** 1.4))[:, :, None]
            output = (
                warped_person.astype(np.float32) * person_alpha
                + output.astype(np.float32) * (1.0 - person_alpha)
            ).astype(np.uint8)

        # Add flying spark particles around the portal rim
        rng = np.random.default_rng(int(age * 45.0) + 509)
        for _ in range(28):
            ang = rng.uniform(0, 2 * math.pi)
            r_spark = radius * rng.uniform(0.78, 1.08)
            sx = int(cx + math.cos(ang) * r_spark)
            sy = int(cy + math.sin(ang) * r_spark * 0.85)
            tx = int(sx - math.sin(ang) * rng.uniform(6, 18))
            ty = int(sy + math.cos(ang) * rng.uniform(6, 18))
            if 0 <= sx < width and 0 <= sy < height:
                cv2.line(output, (sx, sy), (tx, ty), (80, 215, 255), 2, cv2.LINE_AA)

        return output

    def render_vanished(self, frame: np.ndarray, background: np.ndarray, mask: np.ndarray, age: float) -> np.ndarray:
        return background.copy()

