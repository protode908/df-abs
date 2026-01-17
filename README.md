# DFABS v0.1 – first implementation - Surveyor agent only (Discovery prototype)

## Overview

This is the first version and thus intentionally very small:
- 1 agent script: Surveyor
- Discovers files under allow‑listed roots
- Applies strict boundaries (no symlinks (in test), max size, max files)
- Writes outputs:
  - "output/discovery_<CASE>.csv"
  - "bus/10_discovery_report.json" (a simple “FIPA‑ACL‑lite” message)
- in root folder, there is the "make_demo_dataset" script. As it name implies, creates a set of folders/files for testing. All tests from now on are performed based on this truth-set.

## Run (Mac / Linux)
## in bash / terminal
python make_demo_dataset.py
python Surveyor.py

## Notes / limitations (by design)

- No hashing
- No ZIP archive
- No coordinator agent (orchestrator)
- Configuration is hardcoded in Surveyor.py

