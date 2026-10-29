"""Mode 2: Naruto Substitution Jutsu (Kawarimi) — procedural wooden log, chakra smoke & physics bounce."""

from __future__ import annotations

import math

import cv2
import numpy as np


def _generate_kawarimi_log_sprite(height: int = 240, width: int = 180) -> np.ndarray:
    """Procedurally generate an anime-style RGBA wooden substitution log sprite with bark & leaf stub."""
    canvas = np.zeros((height, width, 4), dtype=np.uint8)
    cx, cy = width // 2, height // 2

    # Draw on a rotated coordinate system (-24 degrees diagonal tilt) for dynamic anime look
    y_grid, x_grid = np.mgrid[0:height, 0:width].astype(np.float32)
    angle = math.radians(-22.0)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    dx = x_grid - cx
    dy = y_grid - cy
    rx = dx * cos_a - dy * sin_a
    ry = dx * sin_a + dy * cos_a

    log_half_w = width * 0.22
    log_half_h = height * 0.34

    # Main cylindrical trunk mask
    in_trunk = (np.abs(rx) <= log_half_w) & (np.abs(ry) <= log_half_h)
    # Top and bottom rounded cut faces (ellipses at ry = -log_half_h and ry = +log_half_h)
    end_ry_radius = log_half_w * 0.42
    top_end_dist = ((rx / log_half_w) ** 2) + (((ry + log_half_h) / end_ry_radius) ** 2)
    bot_end_dist = ((rx / log_half_w) ** 2) + (((ry - log_half_h) / end_ry_radius) ** 2)
    in_top_end = top_end_dist <= 1.0
    in_bot_end = bot_end_dist <= 1.0

    body_mask = in_trunk | in_top_end

    # Cel-shaded brown bark across the cylinder width
    norm_x = np.clip((rx + log_half_w) / (2.0 * log_half_w), 0.0, 1.0)
    shade = np.where(norm_x < 0.22, 0.58, np.where(norm_x < 0.72, 0.88, 0.68)).astype(np.float32)
    # Vertical bark grain streaks
    grain = 0.08 * np.sin(rx * 0.65 + np.sin(ry * 0.12) * 1.5)
    bark_factor = np.clip(shade + grain, 0.40, 1.05)

    # BGR bark palette (warm anime wood brown)
    b_ch = np.clip(48 * bark_factor, 0, 255).astype(np.uint8)
    g_ch = np.clip(88 * bark_factor, 0, 255).astype(np.uint8)
    r_ch = np.clip(138 * bark_factor, 0, 255).astype(np.uint8)

    canvas[body_mask, 0] = b_ch[body_mask]
    canvas[body_mask, 1] = g_ch[body_mask]
    canvas[body_mask, 2] = r_ch[body_mask]
    canvas[body_mask, 3] = 255

    # Bottom cut wood face with concentric growth rings (pale tan wood interior)
    ring_r = np.sqrt(np.maximum(0.0, bot_end_dist))
    ring_wave = 0.5 + 0.5 * np.sin(ring_r * 18.0)
    wood_shade = 0.82 + 0.14 * ring_wave
    canvas[in_bot_end, 0] = np.clip(125 * wood_shade[in_bot_end], 0, 255).astype(np.uint8)
    canvas[in_bot_end, 1] = np.clip(178 * wood_shade[in_bot_end], 0, 255).astype(np.uint8)
    canvas[in_bot_end, 2] = np.clip(215 * wood_shade[in_bot_end], 0, 255).astype(np.uint8)
    canvas[in_bot_end, 3] = 255

    # Dark ink outline around the trunk & bottom cut ring
    edge = cv2.Canny(canvas[:, :, 3], 80, 180)
    edge_dilated = cv2.dilate(edge, np.ones((2, 2), dtype=np.uint8), iterations=1) > 0
    canvas[edge_dilated] = (24, 30, 38, 255)

    # Small side branch stub + two green ninja leaves
    stub_pt1 = (int(cx + log_half_w * 0.75), int(cy - log_half_h * 0.25))
    stub_pt2 = (int(cx + log_half_w * 1.35), int(cy - log_half_h * 0.52))
    cv2.line(canvas, stub_pt1, stub_pt2, (36, 66, 105, 255), 7, cv2.LINE_AA)
    cv2.ellipse(canvas, (stub_pt2[0] + 8, stub_pt2[1] - 6), (14, 7), -35, 0, 360, (65, 175, 85, 255), -1, cv2.LINE_AA)
    cv2.ellipse(canvas, (stub_pt2[0] - 4, stub_pt2[1] - 12), (12, 6), -75, 0, 360, (55, 155, 75, 255), -1, cv2.LINE_AA)

    # White paper talisman / seal tag on the front of the log
    tag_x, tag_y = int(cx - 8), int(cy - 14)
    cv2.rectangle(canvas, (tag_x, tag_y), (tag_x + 18, tag_y + 34), (235, 242, 245, 255), -1, cv2.LINE_AA)
    cv2.rectangle(canvas, (tag_x, tag_y), (tag_x + 18, tag_y + 34), (35, 40, 48, 255), 1, cv2.LINE_AA)
    cv2.line(canvas, (tag_x + 9, tag_y + 6), (tag_x + 9, tag_y + 28), (40, 45, 185, 255), 2, cv2.LINE_AA)

    return canvas


class NarutoSubstitutionEffect:
    """Naruto Kawarimi no Jutsu: volumetric chakra smoke cloud, swirling ribbons, and falling wooden log."""

    duration = 1.45

    def __init__(self) -> None:
        self.sprite = _generate_kawarimi_log_sprite()
        self.anchor: tuple[int, int, int] = (320, 240, 180)
        self._resize_cache: dict[int, np.ndarray] = {}

    def reset(self, frame: np.ndarray, mask: np.ndarray) -> None:
        h, w = mask.shape[:2]
        binary = (mask > 0.42).astype(np.uint8)
        num_labels, _, stats, _ = cv2.connectedComponentsWithStats(binary)
        if num_labels <= 1:
            self.anchor = (w // 2, h // 2, int(h * 0.54))
            return
        largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        bx, by, bw, bh, _ = stats[largest]
        size = int(np.clip(bh * 0.56, h * 0.24, h * 0.68))
        cx = int(np.clip(bx + bw * 0.5, size // 3, w - size // 3))
        cy = int(np.clip(by + bh * 0.52, size // 3, h - size // 3))
        self.anchor = (cx, cy, size)

    def _landed_anchor(self, frame_height: int) -> tuple[int, int, int]:
        cx, cy, size = self.anchor
        return cx, max(cy, frame_height - int(round(size * 0.48))), size

    def _falling_anchor(self, frame_height: int, age: float) -> tuple[int, int, int]:
        cx, cy, size = self.anchor
        floor_y = self._landed_anchor(frame_height)[1]
        dist = floor_y - cy
        if dist <= 0 or age <= 0.17:
            return cx, cy, size
        elapsed = age - 0.17
        gravity = frame_height * 3.2
        fall = 0.5 * gravity * elapsed * elapsed
        if fall < dist:
            return cx, cy + int(round(fall)), size
        t_hit = math.sqrt(2.0 * dist / gravity)
        b_age = elapsed - t_hit
        bounce = size * 0.075 * math.exp(-5.0 * b_age) * abs(math.sin(11.0 * b_age))
        return cx, floor_y - int(round(bounce)), size

    def _overlay_log(
        self,
        canvas: np.ndarray,
        anchor: tuple[int, int, int],
        opacity: float = 1.0,
        scale: float = 1.0,
    ) -> None:
        if opacity <= 0.01:
            return
        cx, cy, base_size = anchor
        target_h = max(12, int(base_size * scale))
        target_w = max(12, int(target_h * self.sprite.shape[1] / self.sprite.shape[0]))
        scaled = self._resize_cache.get(target_h)
        if scaled is None:
            scaled = cv2.resize(self.sprite, (target_w, target_h), interpolation=cv2.INTER_AREA)
            self._resize_cache[target_h] = scaled

        x1, y1 = cx - target_w // 2, cy - target_h // 2
        x2, y2 = x1 + target_w, y1 + target_h
        left, top = max(0, x1), max(0, y1)
        right, bot = min(canvas.shape[1], x2), min(canvas.shape[0], y2)
        if left >= right or top >= bot:
            return

        sub = scaled[top - y1 : bot - y1, left - x1 : right - x1]
        alpha = (sub[:, :, 3:4].astype(np.float32) / 255.0) * opacity
        dst = canvas[top:bot, left:right]
        dst[:] = np.clip(
            sub[:, :, :3].astype(np.float32) * alpha + dst.astype(np.float32) * (1.0 - alpha),
            0,
            255,
        ).astype(np.uint8)

    def _draw_chakra_smoke(self, canvas: np.ndarray, age: float, foreground: bool) -> None:
        if age >= self.duration:
            return
        cx, cy, size = self.anchor
        reveal = min(1.0, age / 0.15)
        fade = max(0.0, 1.0 - max(0.0, age - 0.32) / 1.13)
        if fade <= 0.01:
            return

        margin = int(size * 1.38)
        left, top = max(0, cx - margin), max(0, cy - margin)
        right, bot = min(canvas.shape[1], cx + margin + 1), min(canvas.shape[0], cy + margin + 1)
        if left >= right or top >= bot:
            return

        layer = np.zeros((bot - top, right - left, 4), dtype=np.uint8)
        rng = np.random.default_rng(9411 if foreground else 2743)
        radius = size * (0.26 + 0.55 * min(1.0, age))
        for _ in range(22 if foreground else 18):
            ang = rng.uniform(0, 2 * math.pi)
            dist = radius * rng.uniform(0.22, 1.0)
            px = int(cx + math.cos(ang) * dist) - left
            py = int(cy + math.sin(ang) * dist * 0.64 - age * size * 0.14) - top
            puff = max(3, int(size * rng.uniform(0.09, 0.21) * (0.7 + age * 0.68)))
            col = (232, 238, 240, 192) if foreground else (154, 164, 170, 130)
            cv2.ellipse(
                layer,
                (px, py),
                (puff, int(puff * 0.70)),
                rng.uniform(-28, 28),
                0,
                360,
                col,
                -1,
                cv2.LINE_AA,
            )

        # Swirling anime smoke ribbons around the cloud
        for side in (-1, 1):
            rc = (
                int(cx + side * size * 0.14) - left,
                int(cy - size * 0.12 - age * size * 0.09) - top,
            )
            axes = (
                max(3, int(size * (0.29 + age * 0.26))),
                max(3, int(size * (0.09 + age * 0.12))),
            )
            cv2.ellipse(
                layer,
                rc,
                axes,
                side * 16,
                22,
                228,
                (245, 248, 246, 218),
                max(2, int(size * 0.025)),
                cv2.LINE_AA,
            )

        alpha = (layer[:, :, 3:4].astype(np.float32) / 255.0) * reveal * fade
        dst = canvas[top:bot, left:right]
        dst[:] = np.clip(
            layer[:, :, :3].astype(np.float32) * alpha + dst.astype(np.float32) * (1.0 - alpha),
            0,
            255,
        ).astype(np.uint8)

    def render(
        self,
        frame: np.ndarray,
        background: np.ndarray,
        mask: np.ndarray,
        age: float,
        reverse: bool = False,
    ) -> np.ndarray:
        t = max(0.04, self.duration - age if reverse else age)
        if t >= self.duration:
            return self.render_vanished(frame, background, mask, age)

        if t < 0.13:
            alpha = mask * max(0.0, 1.0 - t / 0.13)
            output = (
                frame.astype(np.float32) * alpha[:, :, None]
                + background.astype(np.float32) * (1.0 - alpha[:, :, None])
            ).astype(np.uint8)
        else:
            output = background.copy()

        self._draw_chakra_smoke(output, t, foreground=False)
        log_opacity = min(1.0, max(0.0, (t - 0.05) / 0.15))
        moving_pos = self._falling_anchor(output.shape[0], t)
        self._overlay_log(output, moving_pos, opacity=log_opacity, scale=1.15 - min(t, 0.25) * 0.6)
        self._draw_chakra_smoke(output, t, foreground=True)
        return output

    def render_vanished(
        self, frame: np.ndarray, background: np.ndarray, mask: np.ndarray, age: float
    ) -> np.ndarray:
        output = background.copy()
        self._overlay_log(output, self._landed_anchor(output.shape[0]), opacity=1.0, scale=1.0)
        return output
