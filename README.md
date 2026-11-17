# Supra-Codex Engine (`oi`)

`oi` is a Python/C++ project scaffold for local task processing and orchestration. The current safe MVP provides deterministic local execution of tasks without network access, external services, or source mutation.

## Safe local MVP

Requirements: Python 3.8 or newer. The MVP uses only the Python standard library and does not require installation of the native extension.

Run the example:

```bash
python -m oi_mvp --workers 3 --task alpha --task beta
```

This prints JSON results in input order. Each task is assigned to a local mock worker in round-robin order. With two workers, the first and third tasks are assigned to `Node-1` and the second to `Node-2`.

Run the tests:

```bash
python -m unittest discover -s tests -v
```

The runner is available as `LocalTaskRunner` from `oi_mvp`. It validates worker counts and task values, and returns an empty list for an empty batch.

## Scope and safety

The MVP does not:

- make network requests
- persist task data
- load generated code dynamically
- mutate source files
- claim to be a production distributed runtime

The results are a local demonstration of task scheduling only. `run_supra_master.py` and other experimental mutation/rebuild flows are outside this MVP and should be isolated or reviewed before any execution.

## Repository layout

- `oi_mvp/`: safe local MVP runner and CLI
- `tests/`: unit tests for the MVP
- `bindings/`: pybind11 C++ binding sources
- `core/`, `api/`, `infrastructure/`: experimental support modules
- `CMakeLists.txt`, `pyproject.toml`: native/package build configuration

## CI

The GitHub Actions workflow runs the MVP unit tests on Python 3.8 and 3.11. It does not build the native extension or deploy anything.
