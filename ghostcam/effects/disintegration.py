"""Mode 2: Cosmic Disintegration — silhouette shatters into drifting wind fragments & glowing embers."""

from __future__ import annotations

import numpy as np


class DisintegrationEffect:
    duration = 2.15

    def __init__(self, block_size: int = 6) -> None:
        self.block_size = block_size
        self.base_x = np.empty(0, dtype=np.float32)
        self.base_y = np.empty(0, dtype=np.float32)
        self.colors = np.empty((0, 3), dtype=np.uint8)
        self.delay = np.empty(0, dtype=np.float32)
        self.vx = np.empty(0, dtype=np.float32)
        self.vy = np.empty(0, dtype=np.float32)
        self.freq = np.empty(0, dtype=np.float32)
        self.phase = np.empty(0, dtype=np.float32)
        self.is_ember = np.empty(0, dtype=bool)
        self.width = 0
        self.height = 0

    def reset(self, frame: np.ndarray, mask: np.ndarray) -> None:
        self.height, self.width = frame.shape[:2]
        step = self.block_size
        ys, xs = np.mgrid[0 : self.height : step, 0 : self.width : step]
        valid = mask[ys, xs] > 0.32
        self.base_x = xs[valid].astype(np.float32)
        self.base_y = ys[valid].astype(np.float32)
        self.colors = frame[ys[valid], xs[valid]].astype(np.uint8).copy()

        count = len(self.base_x)
        if count == 0:
            return
        rng = np.random.default_rng(7719)
        nx = (self.base_x - self.base_x.min()) / max(1.0, float(np.ptp(self.base_x)))
        ny = (self.base_y - self.base_y.min()) / max(1.0, float(np.ptp(self.base_y)))
        self.delay = (nx * 0.42 + ny * 0.25 + rng.uniform(0.0, 0.24, count)).astype(np.float32)
        self.vx = rng.uniform(self.width * 0.16, self.width * 0.50, count).astype(np.float32)
        self.vy = rng.uniform(-self.height * 0.24, self.height * 0.07, count).astype(np.float32)
        self.freq = rng.uniform(4.5, 11.5, count).astype(np.float32)
        self.phase = rng.uniform(0.0, 2.0 * np.pi, count).astype(np.float32)
        self.is_ember = rng.random(count) < 0.14
        # Give ember particles a warm gold/cyan glow tint
        self.colors[self.is_ember] = np.array([110, 225, 255], dtype=np.uint8)

    def render(
        self,
        frame: np.ndarray,
        background: np.ndarray,
        mask: np.ndarray,
        age: float,
        reverse: bool = False,
    ) -> np.ndarray:
        output = background.copy()
        if len(self.base_x) == 0 or age >= self.duration:
            return output

        progress = age / self.duration
        dt = np.maximum(0.0, age - self.delay * 0.85)
        life = np.clip(1.0 - dt / (self.duration * 0.72), 0.0, 1.0)
        alive = life > 0.02
        if not np.any(alive):
            return output

        px = self.base_x[alive] + self.vx[alive] * (dt[alive] ** 1.25)
        py = (
            self.base_y[alive]
            + self.vy[alive] * dt[alive]
            + np.sin(dt[alive] * self.freq[alive] + self.phase[alive]) * 8.5 * dt[alive]
        )
        colors = self.colors[alive]
        alphas = life[alive]

        ix = np.round(px).astype(np.int32)
        iy = np.round(py).astype(np.int32)
        valid = (ix >= 0) & (ix < self.width - self.block_size) & (iy >= 0) & (iy < self.height - self.block_size)
        ix, iy, colors, alphas = ix[valid], iy[valid], colors[valid], alphas[valid]

        size = max(2, int(round(self.block_size * (1.0 - 0.28 * progress))))
        for dy in range(size):
            for dx in range(size):
                ry = iy + dy
                rx = ix + dx
                dst = output[ry, rx].astype(np.float32)
                a = alphas[:, None]
                output[ry, rx] = np.clip(colors.astype(np.float32) * a + dst * (1.0 - a), 0, 255).astype(np.uint8)

        return output

    def render_vanished(self, frame: np.ndarray, background: np.ndarray, mask: np.ndarray, age: float) -> np.ndarray:
        return background.copy()

