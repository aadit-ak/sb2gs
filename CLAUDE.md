# sb2gs — goboscript Decompiler

Decompiles Scratch .sb3 files into goboscript .gs text files. By aspizu (github.com/aspizu/sb2gs).

## Setup

```bash
cd /Users/arunk/projects/sb2gs
uv venv && uv pip install -e .
# Activate: source .venv/bin/activate
```

## Usage

```bash
cd /Users/arunk/projects/sb2gs && source .venv/bin/activate
sb2gs input.sb3 output_dir --overwrite
# --verify flag invokes goboscript to check syntax (not semantic equivalence)
```

## Architecture

```
.sb3 ZIP → project.json → per-target decompilation → .gs files + goboscript.toml + assets/
```

Key source locations:
- `src/sb2gs/__init__.py` — CLI entry point (argparse)
- `src/sb2gs/decompile.py` — Main orchestrator: unzips, iterates targets, writes .gs files
- `src/sb2gs/decompile_sprite.py` — `Ctx` class (holds sprite state), property/costume/variable emission
- `src/sb2gs/decompile_events.py` — Event handler decompilation (onflag, on, onclick, onclone, procs)
- `src/sb2gs/decompile_stmt.py` — Statement decompilation; `BLOCKS` dict maps opcodes → signatures
- `src/sb2gs/decompile_expr.py` — Expression/reporter decompilation; `BLOCKS`/`OPERATORS` dicts
- `src/sb2gs/decompile_input.py` — Input decompilation (resolves shadow blocks, literals, reporters)
- `src/sb2gs/decompile_config.py` — Writes `goboscript.toml` from project metadata + TurboWarp config
- `src/sb2gs/costumes.py` — Costume center normalization (SVG viewBox, bitmap paste)
- `src/sb2gs/syntax.py` — Identifier/string/number formatting for .gs syntax
- `src/sb2gs/ast.py` — AST transforms (e.g., operator detection for augmented assignment)
- `src/sb2gs/json_object.py` — Dynamic JSON accessor (attribute-style access to dicts)

## Decompilation Pipeline

1. Unzip .sb3, parse project.json
2. Extract assets to `output/assets/`
3. Fix costume centers (SVG viewBox / bitmap paste)
4. For each target: create `Ctx`, run AST transforms, emit properties/costumes/sounds/vars/events
5. Write `goboscript.toml` with config + layers

## Our Changes

### 2026-03-16

1. **Float rotation center crash** (`costumes.py:48`) — Cast to int: `int(480 - costume.rotationCenterX)`
2. **Missing `looks_switchbackdroptoandwait`** (`decompile_stmt.py:69-74`) — Added to BLOCKS dict
3. **Layer order → goboscript.toml** (`decompile_config.py:53-57,72-73`) — `compute_layers()` sorts sprites by layerOrder
4. **Draggable → onflag event** (`decompile_sprite.py:137-144`) — `decompile_draggable()` emits inside `onflag {}`

### 2026-03-17

5. **Rotation center preservation** (`costumes.py`) — When `fix_vector_center()` removes the
   outer `<g transform="translate(-X,-Y)">`, it now computes the correct new rotation center
   (`original_rc - translate_value`) and embeds it as `data-rotation-center-x/y` attributes
   on the `<svg>` element. goboscript reads these back during .sb3 generation.
   Added helper `_parse_translate()` for SVG transform parsing.

## Adding New Block Support

To decompile a new Scratch block opcode:

**For statements** (blocks that do something):
Add entry to `BLOCKS` dict in `decompile_stmt.py`:
```python
"opcode_name": _("goboscript_name", ["INPUT1", "INPUT2"]),
```

**For reporters** (blocks that return a value):
Add entry to `BLOCKS` dict in `decompile_expr.py`.

**For events** (hat blocks):
Add `decompile_<opcode>` function in `decompile_events.py`.
