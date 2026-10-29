"""Unit test suite for GhostCam Studio effects, gestures, and procedural audio synthesis."""

from __future__ import annotations

from types import SimpleNamespace
import unittest

import numpy as np

from ghostcam.audio import ensure_synthesized_sounds
from ghostcam.config import EFFECT_BY_KEY
from ghostcam.effects import create_effect
from ghostcam.effects.goku import GokuTeleportEffect
from ghostcam.effects.naruto import NarutoSubstitutionEffect, _generate_kawarimi_log_sprite
from ghostcam.effects.normal_dissolve import NormalDissolveEffect
from ghostcam.gestures import (
    detect_forehead_salute,
    detect_horns_gesture,
    detect_joined_palms,
    detect_mode_gesture,
    detect_open_palm,
    detect_peace_sign,
)


def make_hand(center_x: float = 0.5, extended=(True, True, False, False), spread: float = 0.06, thumb_out: bool = False):
    pts = [SimpleNamespace(x=center_x, y=0.55) for _ in range(21)]
    pts[0] = SimpleNamespace(x=center_x, y=0.75)
    pts[4] = SimpleNamespace(x=center_x - (0.18 if thumb_out else 0.04), y=0.52)
    offsets = (-0.06, -0.02, 0.02, 0.06)
    spreads = (-spread, spread, 0.0, spread)
    for idx, (base, off, is_ext, sp) in enumerate(zip((5, 9, 13, 17), offsets, extended, spreads)):
        pts[base] = SimpleNamespace(x=center_x + off, y=0.58)
        if is_ext:
            pts[base + 1] = SimpleNamespace(x=center_x + off + sp * 0.3, y=0.48)
            pts[base + 2] = SimpleNamespace(x=center_x + off + sp * 0.6, y=0.39)
            pts[base + 3] = SimpleNamespace(x=center_x + off + sp, y=0.30)
        else:
            pts[base + 1] = SimpleNamespace(x=center_x + off, y=0.53)
            pts[base + 2] = SimpleNamespace(x=center_x + off, y=0.56)
            pts[base + 3] = SimpleNamespace(x=center_x + off, y=0.60)
    return pts


class GhostCamTests(unittest.TestCase):
    def test_all_effects_render_valid_frames(self):
        frame = np.full((120, 160, 3), 210, dtype=np.uint8)
        bg = np.full((120, 160, 3), 35, dtype=np.uint8)
        mask = np.zeros((120, 160), dtype=np.float32)
        mask[20:100, 45:115] = 1.0

        for key in EFFECT_BY_KEY:
            with self.subTest(effect=key):
                effect = create_effect(key)
                effect.reset(frame, mask)
                mid = effect.render(frame, bg, mask, effect.duration * 0.45, reverse=False)
                vanished = effect.render_vanished(frame, bg, mask, 1.0)
                self.assertEqual(mid.shape, frame.shape)
                self.assertEqual(vanished.shape, frame.shape)
                self.assertEqual(mid.dtype, np.uint8)
                self.assertTrue(np.any(mid != frame))

    def test_naruto_procedural_log_and_substitution(self):
        sprite = _generate_kawarimi_log_sprite()
        self.assertEqual(sprite.shape[2], 4)
        self.assertEqual(int(sprite[:, :, 3].min()), 0)
        self.assertEqual(int(sprite[:, :, 3].max()), 255)

        effect = NarutoSubstitutionEffect()
        frame = np.full((160, 240, 3), 150, dtype=np.uint8)
        bg = np.full_like(frame, 30)
        mask = np.zeros((160, 240), dtype=np.float32)
        mask[30:130, 80:160] = 1.0
        effect.reset(frame, mask)
        mid = effect.render(frame, bg, mask, 0.45)
        vanished = effect.render_vanished(frame, bg, mask, 2.0)
        self.assertTrue(np.any(mid != bg))
        self.assertTrue(np.any(vanished != bg))  # Persistent wooden log on floor

    def test_goku_teleport_forward_and_reverse(self):
        effect = GokuTeleportEffect()
        frame = np.full((120, 160, 3), 200, dtype=np.uint8)
        bg = np.full((120, 160, 3), 25, dtype=np.uint8)
        mask = np.zeros((120, 160), dtype=np.float32)
        mask[20:100, 50:110] = 1.0
        effect.reset(frame, mask)
        fwd = effect.render(frame, bg, mask, 0.20, reverse=False)
        rev = effect.render(frame, bg, mask, 0.20, reverse=True)
        self.assertEqual(fwd.shape, frame.shape)
        self.assertEqual(rev.shape, frame.shape)
        self.assertTrue(np.any(fwd != bg))
        self.assertTrue(np.any(rev != bg))

    def test_normal_dissolve_progression(self):
        effect = NormalDissolveEffect()
        frame = np.full((120, 160, 3), 200, dtype=np.uint8)
        bg = np.full((120, 160, 3), 25, dtype=np.uint8)
        mask = np.zeros((120, 160), dtype=np.float32)
        mask[20:100, 50:110] = 1.0
        effect.reset(frame, mask)
        mid = effect.render(frame, bg, mask, effect.duration * 0.5)
        done = effect.render(frame, bg, mask, effect.duration)
        self.assertTrue(np.any(mid != bg))
        np.testing.assert_array_equal(done, bg)

    def test_gesture_detectors(self):
        v_hand = make_hand(extended=(True, True, False, False), spread=0.05)
        self.assertTrue(detect_peace_sign([v_hand], 640, 480))
        self.assertTrue(detect_mode_gesture("normal", [v_hand], [], 640, 480))
        self.assertTrue(detect_mode_gesture("particles", [v_hand], [], 640, 480))
        self.assertFalse(detect_horns_gesture([v_hand], 640, 480))

        horns_hand = make_hand(extended=(True, False, False, True), spread=0.04)
        self.assertTrue(detect_horns_gesture([horns_hand], 640, 480))
        self.assertTrue(detect_mode_gesture("portal", [horns_hand], [], 640, 480))

        open_hand = make_hand(extended=(True, True, True, True), spread=0.03, thumb_out=True)
        self.assertTrue(detect_open_palm([open_hand], 640, 480))
        self.assertTrue(detect_mode_gesture("stealth", [open_hand], [], 640, 480))

        left_palm = make_hand(center_x=0.46, extended=(True, True, True, True), spread=0.01)
        right_palm = make_hand(center_x=0.54, extended=(True, True, True, True), spread=0.01)
        self.assertTrue(detect_joined_palms([left_palm, right_palm], 640, 480))
        self.assertTrue(detect_mode_gesture("naruto", [left_palm, right_palm], [], 640, 480))

        face = [[SimpleNamespace(x=0.5, y=0.35) for _ in range(468)]]
        face[0][0] = SimpleNamespace(x=0.40, y=0.25)
        face[0][1] = SimpleNamespace(x=0.60, y=0.55)
        face[0][9] = SimpleNamespace(x=0.50, y=0.33)
        face[0][10] = SimpleNamespace(x=0.50, y=0.25)
        salute_hand = make_hand(center_x=0.50, extended=(True, True, False, False), spread=0.005)
        self.assertTrue(detect_forehead_salute([salute_hand], face, 640, 480))
        self.assertTrue(detect_mode_gesture("goku", [salute_hand], face, 640, 480))

    def test_synthesized_sounds_generated(self):
        paths = ensure_synthesized_sounds()
        self.assertEqual(set(paths.keys()), set(EFFECT_BY_KEY.keys()))
        for path in paths.values():
            self.assertTrue(path.is_file())
            self.assertEqual(path.suffix, ".wav")
            self.assertGreater(path.stat().st_size, 10_000)


if __name__ == "__main__":
    unittest.main()
