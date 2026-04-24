# AGENTS.md

## Project Overview

`pyqt5_ela_pro` is a PyQt5 extension widget library based on `PyQt5-ElaWidgetTools`.

## Package Structure

- `pyqt5_ela_pro/` — main package (importable as `from pyqt5_ela_pro import ...`)
- `pyqt5_ela_pro/example/` — widget demo examples (runnable via `python -m pyqt5_ela_pro.example`)
- `example/` — separate standalone demo app using `PyQt5ElaWidgetTools` directly

## Dependencies

- `PyQt5>=5.15.0`

## Installing Dependencies

If you need to install a library, use `uv pip install xxx`.
- `PyQt5-ElaWidgetTools>=0.8.0` (external package, not in this repo)
- `pypinyin>=0.50.0`

Dev: `pytest`, `black`, `flake8`

## Running the Example

```powershell
# Run pyqt5_ela_pro widget examples
uv run python -m pyqt5_ela_pro.example

# Run the standalone demo (from repo root)
cd example && uv run python main.py
```

## Platform

Windows AMD64 only (per `uv.lock` required-markers).

## No Test Infrastructure

No `tests/` directory exists. pytest is listed in dev dependencies but no test commands are configured.

## Linting/Type Checking

No `ruff`, `mypy`, or other linting configs found. Run manually if needed:
```powershell
ty check pyqt5_ela_pro/
ruff format pyqt5_ela_pro/
```

## Build

```powershell
uv build --wheel
```

## Gotchas

- `example/mainwindow.py:62` contains a hardcoded user path: `C:\Users\11737\Pictures\冥契\過去未来1.jpg`
- `example/beforemain.py` runs before the main window — check it when debugging startup issues
- The `icons/packages/fluent_ui_icon_regular.icons` file is a custom binary format used by `svg_icon.py`
