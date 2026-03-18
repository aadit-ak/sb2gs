from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import toml

if TYPE_CHECKING:
    from pathlib import Path

    from .json_object import JSONObject

logger = logging.getLogger(__name__)


@dataclass
class Config:
    std: str | None = None
    bitmap_resolution: int | None = 2
    frame_rate: int | None = None
    max_clones: float | None = None
    no_miscellaneous_limits: bool | None = None
    no_sprite_fencing: bool | None = None
    frame_interpolation: bool | None = None
    high_quality_pen: bool | None = None
    stage_width: int | None = None
    stage_height: int | None = None


def find_turbowarp_config_comment(project: JSONObject) -> str | None:
    stage = next(target for target in project.targets if target.isStage)
    for comment in stage.comments._.values():
        if comment.text.endswith("_twconfig_"):
            return comment.text
    return None


def parse_turbowarp_config_comment(text: str | None) -> dict[str, Any] | None:
    if text is None:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def compute_layers(project: JSONObject) -> list[str]:
    """Compute sprite layer ordering from the project targets."""
    sprites = [t for t in project.targets if not t.isStage]
    sprites.sort(key=lambda t: t.layerOrder)
    return [t.name for t in sprites]


def compute_current_costumes(project: JSONObject) -> dict[str, int]:
    """Collect non-zero currentCostume values for all targets."""
    result: dict[str, int] = {}
    for target in project.targets:
        idx = target.currentCostume
        if idx != 0:
            name = "Stage" if target.isStage else target.name
            result[name] = idx
    return result


def compute_variable_names() -> dict[str, str]:
    """Build sanitized → original name mapping for identifiers that changed.

    Only includes entries where the goboscript identifier differs from the
    original Scratch variable/list name (e.g., "health" → "HEALTH").
    """
    from . import syntax

    result: dict[str, str] = {}
    for original, sanitized in syntax.identifier_map.items():
        if original != sanitized:
            result[sanitized] = original
    return result


def decompile_config(project: JSONObject, output: Path) -> None:
    config = Config()
    data = parse_turbowarp_config_comment(find_turbowarp_config_comment(project)) or {}
    runtime_options = data.get("runtimeOptions", {})
    config.frame_rate = data.get("framerate")
    config.max_clones = runtime_options.get("maxClones")
    config.no_miscellaneous_limits = runtime_options.get("miscLimits") is False
    config.no_sprite_fencing = runtime_options.get("fencing") is False
    config.frame_interpolation = data.get("interpolation") is True
    config.high_quality_pen = data.get("hq") is True
    config.stage_width = data.get("width")
    config.stage_height = data.get("height")
    config_dict = config.__dict__
    config_dict["layers"] = compute_layers(project)
    current_costumes = compute_current_costumes(project)
    if current_costumes:
        config_dict["current_costumes"] = current_costumes
    variable_names = compute_variable_names()
    if variable_names:
        config_dict["variable_names"] = variable_names
    with output.joinpath("goboscript.toml").open("w") as file:
        toml.dump(config_dict, file)
