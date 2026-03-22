from __future__ import annotations

import json
import logging
import shutil
from typing import TYPE_CHECKING
from zipfile import ZipFile

from sb2gs.decompile_config import decompile_config

from . import costumes
from .decompile_sprite import Ctx, decompile_sprite
from .errors import Error
from .json_object import JSONObject

if TYPE_CHECKING:
    from pathlib import Path


def normalize_target(target: JSONObject) -> None:
    target._.setdefault("currentCostume", 0)
    target._.setdefault("volume", 100)
    target._.setdefault("layerOrder", 0)
    target._.setdefault("visible", True)
    target._.setdefault("rotationStyle", "all around")
    if not target.isStage:
        target._.setdefault("x", 0)
        target._.setdefault("y", 0)
        target._.setdefault("size", 100)
        target._.setdefault("direction", 90)
        target._.setdefault("draggable", False)


def normalize_block(block: JSONObject) -> None:
    block._.setdefault("next", None)
    block._.setdefault("parent", None)
    block._.setdefault("inputs", JSONObject({}))
    block._.setdefault("fields", JSONObject({}))
    block._.setdefault("shadow", False)
    block._.setdefault("topLevel", False)
    block._.setdefault("x", 0)
    block._.setdefault("y", 0)


def normalize_project(project: JSONObject) -> None:
    for target in project.targets:
        normalize_target(target)
        for block in target.blocks._.values():
            normalize_block(block)


def decompile(input: Path, output: Path) -> None:
    assets_path = output.joinpath("assets")
    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True, exist_ok=True)
    with ZipFile(input) as zf, zf.open("project.json") as f:
        project = json.load(f, object_hook=JSONObject)
        normalize_project(project)
        for file in zf.filelist:
            if file.filename != "project.json":
                zf.extract(file, assets_path)
    stage = next(target for target in project.targets if target.isStage)
    sprites = [target for target in project.targets if not target.isStage]

    fixed = set()
    for costume in stage.costumes:
        costumes.fix_center(costume, assets_path.joinpath(costume.md5ext), fixed)
    ctx = Ctx(stage)
    with output.joinpath("stage.gs").open("w") as file:
        decompile_sprite(ctx)
        file.write(str(ctx))
    for target in sprites:
        ctx = Ctx(target)
        for costume in target.costumes:
            costumes.fix_center(costume, assets_path.joinpath(costume.md5ext), fixed)
        with output.joinpath(f"{target.name}.gs").open("w") as file:
            decompile_sprite(ctx)
            file.write(str(ctx))
    decompile_config(project, output)
