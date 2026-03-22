from __future__ import annotations

import unittest

from sb2gs.decompile_expr import decompile_expr
from sb2gs.decompile_sprite import Ctx
from sb2gs.json_object import JSONObject


def wrap_json(value):
    if isinstance(value, dict):
        return JSONObject({key: wrap_json(inner) for key, inner in value.items()})
    if isinstance(value, list):
        return [wrap_json(item) for item in value]
    return value


def make_ctx(blocks: dict[str, dict]) -> Ctx:
    target = wrap_json(
        {
            "isStage": False,
            "costumes": [],
            "sounds": [],
            "variables": {},
            "lists": {},
            "blocks": blocks,
            "volume": 100,
            "layerOrder": 0,
            "visible": True,
            "x": 0,
            "y": 0,
            "size": 100,
            "direction": 90,
            "draggable": False,
            "rotationStyle": "all around",
        }
    )
    return Ctx(target)


class DecompileExprMenuTests(unittest.TestCase):
    def assert_expr(self, blocks: dict[str, dict], block_id: str, expected: str) -> None:
        ctx = make_ctx(blocks)
        decompile_expr(ctx, ctx.blocks[block_id])
        self.assertEqual(str(ctx), expected)

    def test_touching_mouse_pointer_stays_shorthand(self) -> None:
        self.assert_expr(
            {
                "touch": {
                    "opcode": "sensing_touchingobject",
                    "next": None,
                    "parent": None,
                    "inputs": {"TOUCHINGOBJECTMENU": [1, "menu"]},
                    "fields": {},
                    "shadow": False,
                    "topLevel": False,
                },
                "menu": {
                    "opcode": "sensing_touchingobjectmenu",
                    "next": None,
                    "parent": "touch",
                    "inputs": {},
                    "fields": {"TOUCHINGOBJECTMENU": ["_mouse_", None]},
                    "shadow": True,
                    "topLevel": False,
                },
            },
            "touch",
            "touching_mouse_pointer()",
        )

    def test_touching_named_sprite_keeps_target(self) -> None:
        self.assert_expr(
            {
                "touch": {
                    "opcode": "sensing_touchingobject",
                    "next": None,
                    "parent": None,
                    "inputs": {"TOUCHINGOBJECTMENU": [1, "menu"]},
                    "fields": {},
                    "shadow": False,
                    "topLevel": False,
                },
                "menu": {
                    "opcode": "sensing_touchingobjectmenu",
                    "next": None,
                    "parent": "touch",
                    "inputs": {},
                    "fields": {"TOUCHINGOBJECTMENU": ["02_task_washDishes", None]},
                    "shadow": True,
                    "topLevel": False,
                },
            },
            "touch",
            'touching("02_task_washDishes")',
        )

    def test_distance_to_mouse_pointer_stays_shorthand(self) -> None:
        self.assert_expr(
            {
                "distance": {
                    "opcode": "sensing_distanceto",
                    "next": None,
                    "parent": None,
                    "inputs": {"DISTANCETOMENU": [1, "menu"]},
                    "fields": {},
                    "shadow": False,
                    "topLevel": False,
                },
                "menu": {
                    "opcode": "sensing_distancetomenu",
                    "next": None,
                    "parent": "distance",
                    "inputs": {},
                    "fields": {"DISTANCETOMENU": ["_mouse_", None]},
                    "shadow": True,
                    "topLevel": False,
                },
            },
            "distance",
            "distance_to_mouse_pointer()",
        )

    def test_distance_to_named_sprite_keeps_target(self) -> None:
        self.assert_expr(
            {
                "distance": {
                    "opcode": "sensing_distanceto",
                    "next": None,
                    "parent": None,
                    "inputs": {"DISTANCETOMENU": [1, "menu"]},
                    "fields": {},
                    "shadow": False,
                    "topLevel": False,
                },
                "menu": {
                    "opcode": "sensing_distancetomenu",
                    "next": None,
                    "parent": "distance",
                    "inputs": {},
                    "fields": {"DISTANCETOMENU": ["01_pet", None]},
                    "shadow": True,
                    "topLevel": False,
                },
            },
            "distance",
            'distance_to("01_pet")',
        )


if __name__ == "__main__":
    unittest.main()
