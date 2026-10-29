"""Interactive graphical launcher menu for GhostCam Studio."""

from __future__ import annotations

import cv2
import numpy as np

from .config import EFFECT_CATALOG


MENU_WINDOW_TITLE = "GhostCam Studio - Select Effect"


def select_effect_dialog() -> str | None:
    """Display an interactive selector window for all catalog modes and return the chosen mode key."""
    width = 780
    card_left, card_right = 52, width - 52
    card_h = 74
    card_gap = 12
    start_top = 98
    height = max(650, start_top + len(EFFECT_CATALOG) * (card_h + card_gap) + 28)

    selected: list[str | None] = [None]
    hovered: list[int] = [-1]
    max_num = len(EFFECT_CATALOG)

    def render_menu() -> np.ndarray:
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        canvas[:] = (20, 22, 28)

        # Header bar
        cv2.putText(
            canvas,
            "GHOSTCAM STUDIO",
            (card_left, 48),
            cv2.FONT_HERSHEY_DUPLEX,
            0.92,
            (242, 246, 250),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            canvas,
            f"Select an effect mode with your mouse or keys 1 - {max_num}  (Press 1-{max_num} anytime in live view to switch)",
            (card_left, 76),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.44,
            (155, 175, 190),
            1,
            cv2.LINE_AA,
        )

        for idx, spec in enumerate(EFFECT_CATALOG):
            top = start_top + idx * (card_h + card_gap)
            bot = top + card_h
            is_hover = hovered[0] == idx
            bg_col = (44, 52, 66) if is_hover else (32, 37, 46)
            border_col = (95, 220, 255) if is_hover else (78, 96, 115)

            cv2.rectangle(canvas, (card_left, top), (card_right, bot), bg_col, -1, cv2.LINE_AA)
            cv2.rectangle(canvas, (card_left, top), (card_right, bot), border_col, 2 if is_hover else 1, cv2.LINE_AA)

            cv2.putText(
                canvas,
                spec.title,
                (card_left + 20, top + 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.66,
                (245, 248, 252),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                canvas,
                spec.subtitle,
                (card_left + 335, top + 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.49,
                (110, 215, 250),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                canvas,
                f"Gesture: {spec.gesture_hint}",
                (card_left + 20, top + 56),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (175, 190, 202),
                1,
                cv2.LINE_AA,
            )

        return canvas

    def on_mouse(event, x, y, flags, userdata) -> None:
        hovered[0] = -1
        if card_left <= x <= card_right:
            for idx in range(len(EFFECT_CATALOG)):
                top = start_top + idx * (card_h + card_gap)
                if top <= y <= top + card_h:
                    hovered[0] = idx
                    if event == cv2.EVENT_LBUTTONUP:
                        selected[0] = EFFECT_CATALOG[idx].key
                    break

    cv2.namedWindow(MENU_WINDOW_TITLE, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(MENU_WINDOW_TITLE, on_mouse)
    try:
        while selected[0] is None:
            cv2.imshow(MENU_WINDOW_TITLE, render_menu())
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
