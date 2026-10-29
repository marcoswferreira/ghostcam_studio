"""Hand and face gesture recognition rules for all 5 GhostCam Studio effects."""

from __future__ import annotations

import numpy as np


def _hand_to_pixels(hand, width: int, height: int) -> np.ndarray | None:
    if len(hand) != 21:
        return None
    pts = np.array([(lm.x * width, lm.y * height) for lm in hand], dtype=np.float32)
    if not np.isfinite(pts).all():
        return None
    return pts


def _finger_extension_ratios(pts: np.ndarray) -> tuple[list[bool], list[bool], float]:
    """Return (extended_flags, folded_flags, palm_scale) for index, middle, ring, pinky."""
    wrist = pts[0]
    palm_scale = max(
        float(np.linalg.norm(pts[5] - pts[17])),
        float(np.linalg.norm(pts[0] - pts[9])),
    )
    if palm_scale < 6.0:
        return [False] * 4, [False] * 4, 0.0

    extended = []
    folded = []
    for base in (5, 9, 13, 17):
        mcp_dist = float(np.linalg.norm(pts[base] - wrist))
        pip_dist = float(np.linalg.norm(pts[base + 1] - wrist))
        tip_dist = float(np.linalg.norm(pts[base + 3] - wrist))
        seg_len = float(np.linalg.norm(np.diff(pts[base : base + 4], axis=0), axis=1).sum())
        straight = float(np.linalg.norm(pts[base + 3] - pts[base])) / max(1e-5, seg_len)
        extended.append(tip_dist > mcp_dist * 1.16 and tip_dist > pip_dist * 1.04 and straight >= 0.76)
        folded.append(tip_dist <= pip_dist * 1.08 or straight < 0.74)

    return extended, folded, palm_scale


def detect_peace_sign(hands, width: int, height: int) -> bool:
    """Mode 2 (Disintegration): Index and middle extended in a V shape, ring & pinky folded."""
    for hand in hands:
        pts = _hand_to_pixels(hand, width, height)
        if pts is None:
            continue
        ext, fold, palm = _finger_extension_ratios(pts)
        if not (ext[0] and ext[1] and fold[2] and fold[3]):
            continue
        if float(np.linalg.norm(pts[8] - pts[12])) >= palm * 0.22:
            return True
    return False


def detect_joined_palms(hands, width: int, height: int) -> bool:
    """Mode 3 (Smoke Bomb): Two hands brought close together with aligned palms."""
    if len(hands) < 2:
        return False
    pts_list = [_hand_to_pixels(h, width, height) for h in hands[:2]]
    if any(p is None for p in pts_list):
        return False
    p0, p1 = pts_list[0], pts_list[1]
    palm0 = p0[[0, 5, 9, 13, 17]].mean(axis=0)
    palm1 = p1[[0, 5, 9, 13, 17]].mean(axis=0)
    scale0 = max(float(np.linalg.norm(p0[5] - p0[17])), float(np.linalg.norm(p0[0] - p0[9])))
    scale1 = max(float(np.linalg.norm(p1[5] - p1[17])), float(np.linalg.norm(p1[0] - p1[9])))
    if min(scale0, scale1) < 8.0:
        return False
    avg_scale = 0.5 * (scale0 + scale1)
    dir0 = p0[9] - p0[0]
    dir1 = p1[9] - p1[0]
    cos_sim = float(np.dot(dir0, dir1) / max(1e-5, np.linalg.norm(dir0) * np.linalg.norm(dir1)))
    tips0 = p0[[8, 12, 16, 20]].mean(axis=0)
    tips1 = p1[[8, 12, 16, 20]].mean(axis=0)
    return (
        cos_sim > 0.22
        and float(np.linalg.norm(palm0 - palm1)) < avg_scale * 1.6
        and float(np.linalg.norm(tips0 - tips1)) < avg_scale * 1.95
    )


def detect_forehead_salute(hands, faces, width: int, height: int) -> bool:
    """Mode 1 (Teleport): Index + middle fingers extended together touching the forehead."""
    if not hands or not faces:
        return False
    face = faces[0]
    if len(face) < 11:
        return False
    xs = np.array([lm.x * width for lm in face], dtype=np.float32)
    ys = np.array([lm.y * height for lm in face], dtype=np.float32)
    fx1, fx2 = float(xs.min()), float(xs.max())
    fy1, fy2 = float(ys.min()), float(ys.max())
    fw = max(12.0, fx2 - fx1)
    fh = max(12.0, fy2 - fy1)
    cx = float(face[10].x * width)
    top_y = min(float(face[10].y * height), fy1)
    brow_y = max(float(face[9].y * height), fy1 + fh * 0.42)

    box_x1, box_x2 = cx - fw * 0.65, cx + fw * 0.65
    box_y1, box_y2 = top_y - fh * 0.35, brow_y + fh * 0.22

    for hand in hands:
        pts = _hand_to_pixels(hand, width, height)
        if pts is None:
            continue
        wrist = pts[0]
        palm = max(float(np.linalg.norm(pts[5] - pts[17])), float(np.linalg.norm(pts[0] - pts[9])))
        if palm < 6.0:
            continue
        idx_reach = float(np.linalg.norm(pts[8] - wrist))
        mid_reach = float(np.linalg.norm(pts[12] - wrist))
        if idx_reach < float(np.linalg.norm(pts[5] - wrist)) * 1.12:
            continue
        if mid_reach < float(np.linalg.norm(pts[9] - wrist)) * 1.12:
            continue
        if float(np.linalg.norm(pts[8] - pts[12])) > palm * 0.95:
            continue
        for joint_idx in (8, 12, 7, 11):
            px, py = float(pts[joint_idx, 0]), float(pts[joint_idx, 1])
            if box_x1 <= px <= box_x2 and box_y1 <= py <= box_y2:
                return True
    return False


def detect_open_palm(hands, width: int, height: int) -> bool:
    """Mode 4 (Optical Stealth Cloak): All 4 main fingers + thumb visibly extended."""
    for hand in hands:
        pts = _hand_to_pixels(hand, width, height)
        if pts is None:
            continue
        ext, _, palm = _finger_extension_ratios(pts)
        if not all(ext):
            continue
        thumb_span = float(np.linalg.norm(pts[4] - pts[17]))
        if thumb_span >= palm * 0.85:
            return True
    return False


def detect_horns_gesture(hands, width: int, height: int) -> bool:
    """Mode 5 (Dimensional Portal): Rock-On / Horns gesture (index + pinky extended, middle + ring folded)."""
    for hand in hands:
        pts = _hand_to_pixels(hand, width, height)
        if pts is None:
            continue
        ext, fold, palm = _finger_extension_ratios(pts)
        if ext[0] and fold[1] and fold[2] and ext[3] and palm >= 8.0:
            return True
    return False


def detect_mode_gesture(mode: str, hands, faces, width: int, height: int) -> bool:
    """Dispatch gesture detection for the active studio mode."""
    if mode == "teleport":
        return detect_forehead_salute(hands, faces, width, height)
    if mode == "disintegration":
        return detect_peace_sign(hands, width, height)
    if mode == "smoke":
        return detect_joined_palms(hands, width, height)
    if mode == "stealth":
        return detect_open_palm(hands, width, height)
    if mode == "portal":
        return detect_horns_gesture(hands, width, height)
    return False
