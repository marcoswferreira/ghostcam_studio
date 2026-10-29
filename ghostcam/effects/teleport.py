"""Mode 1: Instant Teleport — vertical anime speed lines and spatial squeeze."""

from __future__ import annotations

import cv2
import numpy as np


class TeleportEffect:
    duration = 0.52

    def reset(self, frame: np.ndarray, mask: np.ndarray) -> None:
        pass

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
        binary = (mask > 0.25).astype(np.uint8)
        pts = cv2.findNonZero(binary)
        if pts is None:
            return frame.copy() if (reverse and age >= self.duration) else background.copy()

        bx, by, bw, bh = cv2.boundingRect(pts)
        cx = bx + bw * 0.5

        if progress < 0.52:
            t_local = progress / 0.52
            squeeze = max(0.10, 1.0 - 0.85 * (t_local ** 2))
            x_coords = np.arange(width, dtype=np.float32)
            src_x = (x_coords - cx) / squeeze + cx
            map_x = np.broadcast_to(src_x[None, :], (height, width)).astype(np.float32)
            map_y = np.broadcast_to(np.arange(height, dtype=np.float32)[:, None], (height, width)).astype(np.float32)
            warped_frame = cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            warped_mask = cv2.remap(mask, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            alpha = warped_mask * (1.0 - 0.65 * t_local)
            output = (
                warped_frame.astype(np.float32) * alpha[:, :, None]
                + background.astype(np.float32) * (1.0 - alpha[:, :, None])
            ).astype(np.uint8)
            active_mask = warped_mask
        else:
            output = background.copy()
            t_local = (progress - 0.52) / 0.48
            squeeze = max(0.06, 0.22 * (1.0 - t_local))
            x_coords = np.arange(width, dtype=np.float32)
            src_x = (x_coords - cx) / squeeze + cx
            map_x = np.broadcast_to(src_x[None, :], (height, width)).astype(np.float32)
            map_y = np.broadcast_to(np.arange(height, dtype=np.float32)[:, None], (height, width)).astype(np.float32)
            active_mask = cv2.remap(mask, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

        line_intensity = float(np.sin(progress * np.pi))
        if line_intensity > 0.04:
            rng = np.random.default_rng(int(age * 60.0) + 307)
            overlay = output.copy()
            num_lines = max(20, int(bw * 0.45))
            x_min = max(0, int(cx - bw * 0.55))
            x_max = min(width - 1, int(cx + bw * 0.55))
            if x_max > x_min:
                for _ in range(num_lines):
                    lx = int(rng.integers(x_min, x_max + 1))
                    seg_h = int(rng.integers(max(12, bh // 5), max(24, int(bh * 0.95))))
                    ly1 = int(rng.integers(max(0, by - 12), min(height - 1, by + bh)))
                    ly2 = min(height - 1, ly1 + seg_h)
                    color = (16, 20, 26) if rng.random() < 0.45 else (255, 250, 220)
                    thickness = 1 if rng.random() < 0.65 else 2
                    cv2.line(overlay, (lx, ly1), (lx, ly2), color, thickness, cv2.LINE_AA)

            blend = np.clip((active_mask > 0.18).astype(np.float32) * line_intensity * 0.92, 0.0, 1.0)
            output = (
                overlay.astype(np.float32) * blend[:, :, None]
                + output.astype(np.float32) * (1.0 - blend[:, :, None])
            ).astype(np.uint8)

        return output

    def render_vanished(self, frame: np.ndarray, background: np.ndarray, mask: np.ndarray, age: float) -> np.ndarray:
        return background.copy()
