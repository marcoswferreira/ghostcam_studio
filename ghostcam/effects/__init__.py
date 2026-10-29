"""Effect registry for GhostCam Studio."""

from __future__ import annotations

from .disintegration import DisintegrationEffect
from .portal import DimensionalPortalEffect
from .smoke_bomb import SmokeBombEffect
from .stealth_cloak import StealthCloakEffect
from .teleport import TeleportEffect


def create_effect(mode_key: str):
    if mode_key == "teleport":
        return TeleportEffect()
    if mode_key == "disintegration":
        return DisintegrationEffect()
    if mode_key == "smoke":
        return SmokeBombEffect()
    if mode_key == "stealth":
        return StealthCloakEffect()
    if mode_key == "portal":
        return DimensionalPortalEffect()
    raise ValueError(f"Unknown effect mode: {mode_key}")
