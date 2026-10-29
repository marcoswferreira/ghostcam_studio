"""Effect registry for GhostCam Studio."""

from __future__ import annotations

from .disintegration import DisintegrationEffect
from .goku import GokuTeleportEffect
from .naruto import NarutoSubstitutionEffect
from .normal_dissolve import NormalDissolveEffect
from .portal import DimensionalPortalEffect
from .smoke_bomb import SmokeBombEffect
from .stealth_cloak import StealthCloakEffect
from .teleport import TeleportEffect


def create_effect(mode_key: str):
    if mode_key == "normal":
        return NormalDissolveEffect()
    if mode_key == "naruto":
        return NarutoSubstitutionEffect()
    if mode_key in ("particles", "disintegration"):
        return DisintegrationEffect()
    if mode_key == "goku":
        return GokuTeleportEffect()
    if mode_key == "teleport":
        return TeleportEffect()
    if mode_key == "smoke":
        return SmokeBombEffect()
    if mode_key == "stealth":
        return StealthCloakEffect()
    if mode_key == "portal":
        return DimensionalPortalEffect()
    raise ValueError(f"Unknown effect mode: {mode_key}")
