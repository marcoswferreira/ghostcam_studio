"""Mode 3: Ninja Smoke Bomb — volumetric smoke cloud and procedural decoy scroll."""

from __future__ import annotations

import math

import cv2
import numpy as np


def _build_decoy_scroll_sprite(height: int = 220, width: int = 110) -> np.ndarray:
    """Create a procedural RGBA ninja substitution scroll/totem sprite."""
    sprite = np.zeros((height, width, 4), dtype=np.uint8)
    cx = width // 2
    body_w = int(width * 0.56)
    body_top = int(height * 0.14)
    body_bot = int(height * 0.86)

    # Wooden/crimson scroll cylinder with cel-shaded gradient
    for x in range(cx - body_w // 2, cx + body_w // 2):
        rel = (x - (cx - body_w // 2)) / max(1, body_w)
        shade = 0.65 + 0.35 * math.sin(rel * math.pi)
        b = int(42 * shade)
        g = int(58 * shade)
        r = int(175 * shade)
        cv2.line(sprite, (x, body_top), (x, body_bot), (b, g, r, 255), 1)

    # Center parchment band
    band_top = int(height * 0.36)
    band_bot = int(height * 0.64)
    cv2.rectangle(
        sprite,
        (cx - body_w // 2 + 2, band_top),
        (cx + body_w // 2 - 2, band_bot),
        (210, 232, 242, 255),
        -1,
    )
    # Dark ink seal symbol on band
    cv2.circle(sprite, (cx, (band_top + band_bot) // 2), int(body_w * 0.22), (30, 35, 45, 255), 2, cv2.LINE_AA)

    # Gold/wooden end caps & dowel rods
    cap_h = int(height * 0.06)
    for y_cap in (body_top, body_bot - cap_h):
        cv2.rectangle(
            sprite,
            (cx - int(body_w * 0.58), y_cap),
            (cx + int(body_w * 0.58), y_cap + cap_h),
            (55, 165, 220, 255),
            -1,
        )
    # Top and bottom wooden roller handles
    cv2.rectangle(sprite, (cx - int(width * 0.42), body_top + 2), (cx + int(width * 0.42), body_top + cap_h - 2), (45, 95, 140, 255), -1)
    cv2.rectangle(sprite, (cx - int(width * 0.42), body_bot - cap_h + 2), (cx + int(width * 0.42), body_bot - 2), (45, 95, 140, 255), -1)

    return sprite


class SmokeBombEffect:
    duration = 1.45

    def __init__(self) -> None:
        self.sprite = _build_decoy_scroll_sprite()
        self.anchor: tuple[int, int, int] = (320, 240, 180)

    def reset(self, frame: np.ndarray, mask: np.ndarray) -> None:
        h, w = mask.shape[:2]
        binary = (mask > 0.42).astype(np.uint8)
        pts = cv2.findNonZero(binary)
        if pts is None:
            self.anchor = (w // 2, h // 2, int(h * 0.45))
            return
        bx, by, bw, bh = cv2.boundingRect(pts)
        size = int(np.clip(bh * 0.48, h * 0.22, h * 0.62))
        cx = int(np.clip(bx + bw * 0.5, size // 2, w - size // 2))
        cy = int(np.clip(by + bh * 0.5, size // 2, h - size // 2))
        self.anchor = (cx, cy, size)

    def _falling_anchor(self, frame_height: int, age: float) -> tuple[int, int, int]:
        cx, cy, size = self.anchor
        floor_y = max(cy, frame_height - int(size * 0.52))
        dist = floor_y - cy
        if dist <= 0 or age <= 0.16:
            return cx, cy, size
        elapsed = age - 0.16
        gravity = frame_height * 3.1
        fall = 0.5 * gravity * elapsed * elapsed
        if fall < dist:
            return cx, cy + int(round(fall)), size
        t_hit = math.sqrt(2.0 * dist / gravity)
        b_age = elapsed - t_hit
        bounce = size * 0.08 * math.exp(-5.0 * b_age) * abs(math.sin(11.0 * b_age))
        return cx, floor_y - int(round(bounce)), size

    def _overlay_sprite(self, canvas: np.ndarray, anchor: tuple[int, int, int], opacity: float = 1.0) -> None:
        if opacity <= 0.01:
            return
        cx, cy, target_h = anchor
        target_h = max(12, int(target_h))
        target_w = max(8, int(target_h * self.sprite.shape[1] / self.sprite.shape[0]))
        resized = cv2.resize(self.sprite, (target_w, target_h), interpolation=cv2.INTER_AREA)

        x1, y1 = cx - target_w // 2, cy - target_h // 2
        x2, y2 = x1 + target_w, y1 + target_h
        left, top = max(0, x1), max(0, y1)
        right, bot = min(canvas.shape[1], x2), min(canvas.shape[0], y2)
        if left >= right or top >= bot:
            return

        sub = resized[top - y1 : bot - y1, left - x1 : right - x1]
        alpha = (sub[:, :, 3:4].astype(np.float32) / 255.0) * opacity
        dst = canvas[top:bot, left:right]
        dst[:] = np.clip(sub[:, :, :3].astype(np.float32) * alpha + dst.astype(np.float32) * (1.0 - alpha), 0, 255).astype(np.uint8)

    def _draw_smoke(self, canvas: np.ndarray, age: float, front: bool) -> None:
        if age >= self.duration:
            return
        cx, cy, size = self.anchor
        reveal = min(1.0, age / 0.14)
        fade = max(0.0, 1.0 - max(0.0, age - 0.30) / 1.15)
        if fade <= 0.01:
            return

        margin = int(size * 1.45)
        left, top = max(0, cx - margin), max(0, cy - margin)
        right, bot = min(canvas.shape[1], cx + margin), min(canvas.shape[0], cy + margin)
        if left >= right or top >= bot:
            return

        layer = np.zeros((bot - top, right - left, 4), dtype=np.uint8)
        rng = np.random.default_rng(8821 if front else 3319)
        radius = size * (0.28 + 0.58 * min(1.0, age))
        for _ in range(24 if front else 18):
            ang = rng.uniform(0, 2 * math.pi)
            dist = radius * rng.uniform(0.2, 1.0)
            px = int(cx + math.cos(ang) * dist) - left
            py = int(cy + math.sin(ang) * dist * 0.65 - age * size * 0.15) - top
            puff = max(3, int(size * rng.uniform(0.10, 0.22) * (0.7 + age * 0.65)))
            col = (238, 242, 245, 195) if front else (155, 165, 172, 135)
            cv2.ellipse(layer, (px, py), (puff, int(puff * 0.72)), rng.uniform(-30, 30), 0, 360, col, -1, cv2.LINE_AA)

        alpha = (layer[:, :, 3:4].astype(np.float32) / 255.0) * reveal * fade
        dst = canvas[top:bot, left:right]
        dst[:] = np.clip(layer[:, :, :3].astype(np.float32) * alpha + dst.astype(np.float32) * (1.0 - alpha), 0, 255).astype(np.uint8)

    def render(
        self,
        frame: np.ndarray,
        background: np.ndarray,
        mask: np.ndarray,
        age: float,
        reverse: bool = False,
    ) -> np.ndarray:
        if age < 0.12:
            alpha = mask * max(0.0, 1.0 - age / 0.12)
            output = (
                frame.astype(np.float32) * alpha[:, :, None]
                + background.astype(np.float32) * (1.0 - alpha[:, :, None])
            ).astype(np.uint8)
        else:
            output = background.copy()

        self._draw_smoke(output, age, front=False)
        pos = self._falling_anchor(output.shape[0], age)
        self._overlay_sprite(output, pos, opacity=min(1.0, max(0.0, (age - 0.04) / 0.14)))
        self._draw_smoke(output, age, front=True)
        return output

    def render_vanished(self, frame: np.ndarray, background: np.ndarray, mask: np.ndarray, age: float) -> np.ndarray:
        output = background.copy()
        cx, cy, size = self.anchor
        landed = (cx, max(cy, output.shape[0] - int(size * 0.52)), size)
        self._overlay_sprite(output, landed, opacity=1.0)
        return output
