"""Interactive graphical launcher menu for GhostCam Studio."""

from __future__ import annotations

import math

import cv2
import numpy as np

from .config import EFFECT_CATALOG, EffectSpec


MENU_WINDOW_TITLE = "GhostCam Studio - Select Effect"

MENU_WIDTH = 980
MENU_HEIGHT = 650

# Layout grid constants (2 columns x 4 rows)
GRID_LEFT = 38
GRID_TOP = 108
COL_GAP = 20
ROW_GAP = 14
CARD_W = (MENU_WIDTH - GRID_LEFT * 2 - COL_GAP) // 2
CARD_H = 114

# Per-effect BGR accent colors
EFFECT_ACCENTS: dict[str, tuple[int, int, int]] = {
    "normal": (255, 215, 75),     # Solar Cyan-Blue
    "naruto": (60, 145, 255),     # Chakra Orange
    "particles": (210, 115, 255), # Cosmic Pink-Violet
    "goku": (55, 215, 255),       # Dragon Ball Ki Gold
    "stealth": (185, 245, 70),    # Predator Cyber Teal
    "portal": (255, 110, 175),    # Dimensional Magenta-Violet
    "smoke": (95, 105, 255),      # Ninja Crimson
}


def _clean_title(raw_title: str) -> str:
    """Strip the leading number prefix (e.g. '1  NORMAL VANISH' -> 'NORMAL VANISH')."""
    parts = raw_title.split("  ", 1)
    return parts[1].strip() if len(parts) == 2 else raw_title.strip()


def _draw_rounded_rect(
    canvas: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    radius: int,
    fill_color: tuple[int, int, int] | None = None,
    border_color: tuple[int, int, int] | None = None,
    thickness: int = 1,
) -> None:
    """Draw an anti-aliased rounded rectangle on an OpenCV canvas."""
    r = max(2, min(radius, (x2 - x1) // 2, (y2 - y1) // 2))
    if fill_color is not None:
        cv2.rectangle(canvas, (x1 + r, y1), (x2 - r, y2), fill_color, -1, cv2.LINE_AA)
        cv2.rectangle(canvas, (x1, y1 + r), (x2, y2 - r), fill_color, -1, cv2.LINE_AA)
        cv2.circle(canvas, (x1 + r, y1 + r), r, fill_color, -1, cv2.LINE_AA)
        cv2.circle(canvas, (x2 - r, y1 + r), r, fill_color, -1, cv2.LINE_AA)
        cv2.circle(canvas, (x1 + r, y2 - r), r, fill_color, -1, cv2.LINE_AA)
        cv2.circle(canvas, (x2 - r, y2 - r), r, fill_color, -1, cv2.LINE_AA)

    if border_color is not None and thickness > 0:
        cv2.line(canvas, (x1 + r, y1), (x2 - r, y1), border_color, thickness, cv2.LINE_AA)
        cv2.line(canvas, (x1 + r, y2), (x2 - r, y2), border_color, thickness, cv2.LINE_AA)
        cv2.line(canvas, (x1, y1 + r), (x1, y2 - r), border_color, thickness, cv2.LINE_AA)
        cv2.line(canvas, (x2, y1 + r), (x2, y2 - r), border_color, thickness, cv2.LINE_AA)
        cv2.ellipse(canvas, (x1 + r, y1 + r), (r, r), 180, 0, 90, border_color, thickness, cv2.LINE_AA)
        cv2.ellipse(canvas, (x2 - r, y1 + r), (r, r), 270, 0, 90, border_color, thickness, cv2.LINE_AA)
        cv2.ellipse(canvas, (x2 - r, y2 - r), (r, r), 0, 0, 90, border_color, thickness, cv2.LINE_AA)
        cv2.ellipse(canvas, (x1 + r, y2 - r), (r, r), 90, 0, 90, border_color, thickness, cv2.LINE_AA)


def _draw_effect_icon(canvas: np.ndarray, key: str, cx: int, cy: int, accent: tuple[int, int, int]) -> None:
    """Draw a custom procedural vector emblem for each effect inside a 46x46 badge."""
    if key == "normal":
        # Dissolve wave lines + sparkles
        for dy, w in ((-8, 11), (0, 14), (8, 9)):
            cv2.line(canvas, (cx - w, cy + dy), (cx + w, cy + dy), accent, 2, cv2.LINE_AA)
        cv2.circle(canvas, (cx + 10, cy - 10), 2, (240, 250, 255), -1, cv2.LINE_AA)
        cv2.circle(canvas, (cx - 9, cy + 10), 2, (240, 250, 255), -1, cv2.LINE_AA)
    elif key == "naruto":
        # Kawarimi spiral / wooden log emblem
        cv2.ellipse(canvas, (cx, cy), (13, 13), 0, 20, 315, accent, 2, cv2.LINE_AA)
        cv2.ellipse(canvas, (cx, cy), (7, 7), 0, 60, 340, (235, 245, 255), 2, cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy), 2, accent, -1, cv2.LINE_AA)
    elif key == "particles":
        # Drifting wind particle cluster
        offsets = [(-9, -6, 3), (-2, 4, 3), (6, -8, 2), (10, 2, 2), (-7, 9, 2), (3, 10, 1)]
        for ox, oy, rad in offsets:
            col = (240, 245, 255) if rad <= 2 else accent
            cv2.circle(canvas, (cx + ox, cy + oy), rad, col, -1, cv2.LINE_AA)
    elif key == "goku":
        # Instant Transmission vertical speed lines & ki spark
        for ox, h_half in ((-10, 8), (-4, 14), (3, 12), (9, 7)):
            col = (245, 252, 255) if ox == -4 else accent
            cv2.line(canvas, (cx + ox, cy - h_half), (cx + ox, cy + h_half), col, 2, cv2.LINE_AA)
    elif key == "stealth":
        # Hexagonal optical prism
        pts = np.array(
            [
                [cx + int(14 * math.cos(math.radians(60 * i - 30))), cy + int(14 * math.sin(math.radians(60 * i - 30)))]
                for i in range(6)
            ],
            dtype=np.int32,
        )
        cv2.polylines(canvas, [pts], True, accent, 2, cv2.LINE_AA)
        cv2.line(canvas, (cx - 8, cy), (cx + 8, cy), (225, 250, 250), 1, cv2.LINE_AA)
    elif key == "portal":
        # Swirling dimensional vortex rings
        cv2.ellipse(canvas, (cx, cy), (14, 9), -28, 0, 360, accent, 2, cv2.LINE_AA)
        cv2.ellipse(canvas, (cx, cy), (8, 5), 32, 0, 360, (240, 240, 255), 1, cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy), 2, accent, -1, cv2.LINE_AA)
    else:
        # Ninja scroll cylinder
        cv2.rectangle(canvas, (cx - 6, cy - 12), (cx + 6, cy + 12), accent, 2, cv2.LINE_AA)
        cv2.line(canvas, (cx - 10, cy - 12), (cx + 10, cy - 12), (235, 245, 255), 2, cv2.LINE_AA)
        cv2.line(canvas, (cx - 10, cy + 12), (cx + 10, cy + 12), (235, 245, 255), 2, cv2.LINE_AA)


def _card_bounds(idx: int) -> tuple[int, int, int, int]:
    """Return (x1, y1, x2, y2) for a card index (0..7) in the 2x4 Bento grid."""
    col = idx % 2
    row = idx // 2
    x1 = GRID_LEFT + col * (CARD_W + COL_GAP)
    y1 = GRID_TOP + row * (CARD_H + ROW_GAP)
    return x1, y1, x1 + CARD_W, y1 + CARD_H


def _draw_effect_card(canvas: np.ndarray, idx: int, spec: EffectSpec, is_hover: bool) -> None:
    x1, y1, x2, y2 = _card_bounds(idx)
    accent = EFFECT_ACCENTS.get(spec.key, (255, 210, 80))

    bg_color = (50, 38, 32) if is_hover else (34, 26, 22)
    border_color = accent if is_hover else (76, 60, 50)
    border_thick = 2 if is_hover else 1

    _draw_rounded_rect(canvas, x1, y1, x2, y2, radius=12, fill_color=bg_color, border_color=border_color, thickness=border_thick)

    # Left vertical accent bar inside the card
    bar_h = 56 if is_hover else 38
    bar_y1 = (y1 + y2 - bar_h) // 2
    cv2.line(canvas, (x1 + 4, bar_y1), (x1 + 4, bar_y1 + bar_h), accent, 3, cv2.LINE_AA)

    # Icon badge box on the left
    icon_box_x1, icon_box_y1 = x1 + 18, y1 + 18
    icon_box_x2, icon_box_y2 = icon_box_x1 + 48, icon_box_y1 + 48
    icon_bg = tuple(int(c * 0.22 + 24) for c in accent)
    _draw_rounded_rect(
        canvas,
        icon_box_x1,
        icon_box_y1,
        icon_box_x2,
        icon_box_y2,
        radius=10,
        fill_color=icon_bg,
        border_color=accent if is_hover else (64, 76, 96),
        thickness=1,
    )
    _draw_effect_icon(canvas, spec.key, (icon_box_x1 + icon_box_x2) // 2, (icon_box_y1 + icon_box_y2) // 2, accent)

    # Keycap shortcut badge [1] - [7] at top-right
    key_x2, key_y1 = x2 - 16, y1 + 15
    key_x1, key_y2 = key_x2 - 32, key_y1 + 26
    key_bg = accent if is_hover else (38, 45, 60)
    key_fg = (15, 18, 24) if is_hover else (235, 242, 250)
    _draw_rounded_rect(canvas, key_x1, key_y1, key_x2, key_y2, radius=6, fill_color=key_bg, border_color=accent, thickness=1)
    cv2.putText(
        canvas,
        str(spec.number),
        (key_x1 + 10, key_y1 + 19),
        cv2.FONT_HERSHEY_DUPLEX,
        0.52,
        key_fg,
        1,
        cv2.LINE_AA,
    )

    # Duration pill next to the keycap badge
    dur_text = f"{spec.duration:.2f}s"
    cv2.putText(
        canvas,
        dur_text,
        (key_x1 - 54, key_y1 + 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
        (140, 155, 175),
        1,
        cv2.LINE_AA,
    )

    # Title & Subtitle (stacked cleanly to prevent any overlap)
    text_x = icon_box_x2 + 16
    clean_name = _clean_title(spec.title)
    cv2.putText(
        canvas,
        clean_name,
        (text_x, y1 + 35),
        cv2.FONT_HERSHEY_DUPLEX,
        0.58,
        (246, 249, 255),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        canvas,
        spec.subtitle,
        (text_x, y1 + 58),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.46,
        accent,
        1,
        cv2.LINE_AA,
    )

    # Subtle divider line above gesture hint
    cv2.line(canvas, (x1 + 18, y1 + 76), (x2 - 18, y1 + 76), (56, 44, 38), 1, cv2.LINE_AA)

    # Gesture hint row at bottom of card
    cv2.circle(canvas, (x1 + 24, y1 + 94), 3, accent, -1, cv2.LINE_AA)
    cv2.putText(
        canvas,
        spec.gesture_hint,
        (x1 + 35, y1 + 98),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
        (215, 200, 190) if is_hover else (182, 168, 156),
        1,
        cv2.LINE_AA,
    )


def _draw_shortcuts_card(canvas: np.ndarray, idx: int) -> None:
    """Draw the 8th Bento grid card summarizing live studio keyboard controls."""
    x1, y1, x2, y2 = _card_bounds(idx)
    _draw_rounded_rect(
        canvas,
        x1,
        y1,
        x2,
        y2,
        radius=12,
        fill_color=(28, 21, 18),
        border_color=(68, 54, 46),
        thickness=1,
    )
    cv2.putText(
        canvas,
        "LIVE FEED CONTROLS",
        (x1 + 20, y1 + 30),
        cv2.FONT_HERSHEY_DUPLEX,
        0.52,
        (235, 215, 200),
        1,
        cv2.LINE_AA,
    )
    shortcuts = (
        ("1-7", "Switch Mode", x1 + 20, y1 + 62, 42),
        ("V / R", "Vanish / Return", x1 + 165, y1 + 62, 50),
        ("F", "Fullscreen", x1 + 332, y1 + 62, 26),
        ("SPACE", "Recalibrate", x1 + 20, y1 + 92, 56),
        ("Q / ESC", "Quit Studio", x1 + 165, y1 + 92, 62),
    )
    for key_lbl, desc, sx, sy, offset in shortcuts:
        cv2.putText(canvas, f"[{key_lbl}]", (sx, sy), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 215, 75), 1, cv2.LINE_AA)
        cv2.putText(canvas, desc, (sx + offset, sy), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (175, 162, 152), 1, cv2.LINE_AA)


def render_launcher_canvas(hovered_idx: int = -1) -> np.ndarray:
    """Render the complete GhostCam Studio launcher window as a BGR image."""
    canvas = np.zeros((MENU_HEIGHT, MENU_WIDTH, 3), dtype=np.uint8)
    # Subtle vertical dark studio gradient background
    y_grad = np.linspace(14, 22, MENU_HEIGHT, dtype=np.float32)[:, None]
    canvas[:, :, 0] = np.clip(y_grad + 6, 0, 255).astype(np.uint8)
    canvas[:, :, 1] = np.clip(y_grad + 2, 0, 255).astype(np.uint8)
    canvas[:, :, 2] = np.clip(y_grad, 0, 255).astype(np.uint8)

    # Top glowing accent strip
    cv2.line(canvas, (0, 0), (MENU_WIDTH, 0), (255, 205, 65), 3, cv2.LINE_AA)

    # Studio Header
    cv2.putText(
        canvas,
        "GHOSTCAM STUDIO",
        (GRID_LEFT, 48),
        cv2.FONT_HERSHEY_DUPLEX,
        0.92,
        (246, 250, 255),
        2,
        cv2.LINE_AA,
    )

    # Status pill next to title
    pill_x1, pill_y1 = GRID_LEFT + 305, 25
    pill_x2, pill_y2 = pill_x1 + 142, 51
    _draw_rounded_rect(
        canvas,
        pill_x1,
        pill_y1,
        pill_x2,
        pill_y2,
        radius=12,
        fill_color=(24, 38, 48),
        border_color=(255, 210, 75),
        thickness=1,
    )
    cv2.circle(canvas, (pill_x1 + 15, pill_y1 + 13), 4, (120, 245, 150), -1, cv2.LINE_AA)
    cv2.putText(
        canvas,
        "LOCAL AI VFX",
        (pill_x1 + 27, pill_y1 + 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.43,
        (230, 245, 255),
        1,
        cv2.LINE_AA,
    )

    max_num = len(EFFECT_CATALOG)
    cv2.putText(
        canvas,
        f"Click any effect card or press keys 1 - {max_num} to launch immediately",
        (GRID_LEFT, 78),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (158, 174, 194),
        1,
        cv2.LINE_AA,
    )

    for idx, spec in enumerate(EFFECT_CATALOG):
        _draw_effect_card(canvas, idx, spec, is_hover=(hovered_idx == idx))

    if len(EFFECT_CATALOG) == 7:
        _draw_shortcuts_card(canvas, 7)

    return canvas


def select_effect_dialog() -> str | None:
    """Display an interactive selector window for all catalog modes and return the chosen mode key."""
    selected: list[str | None] = [None]
    hovered: list[int] = [-1]

    def on_mouse(event, x, y, flags, userdata) -> None:
        hovered[0] = -1
        for idx in range(len(EFFECT_CATALOG)):
            x1, y1, x2, y2 = _card_bounds(idx)
            if x1 <= x <= x2 and y1 <= y <= y2:
                hovered[0] = idx
                if event == cv2.EVENT_LBUTTONUP:
                    selected[0] = EFFECT_CATALOG[idx].key
                break

    cv2.namedWindow(MENU_WINDOW_TITLE, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(MENU_WINDOW_TITLE, on_mouse)
    try:
        while selected[0] is None:
            cv2.imshow(MENU_WINDOW_TITLE, render_launcher_canvas(hovered[0]))
            key = cv2.waitKey(30) & 0xFF
            if key in (ord("q"), 27):
                return None
            for spec in EFFECT_CATALOG:
                if key == ord(str(spec.number)):
                    selected[0] = spec.key
                    break
            if cv2.getWindowProperty(MENU_WINDOW_TITLE, cv2.WND_PROP_VISIBLE) < 1:
                return None
        return selected[0]
    finally:
        cv2.destroyWindow(MENU_WINDOW_TITLE)
