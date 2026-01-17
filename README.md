# DFABS v0.2 - two agents now, Surveyor + HasherPacker (Hash + ZIP)

## Overview

Changes from v0.1:
- Added a second agent: HasherPacker
- Introduced a shared helper module: `common.py`
- Output now includes:
  - SHA‑256 hashes (integrity)
  - ZIP archive (preservation)

The “agent communication” is still file‑based JSON:
- Surveyor writes: `bus/10_discovery_report.json`
- HasherPacker reads that and writes: `bus/20_hash_result.json`

- in root folder, there is the "make_demo_dataset" script. As it name implies, creates a set of folders/files for testing. All tests from now on are performed based on this truth-set.

IMPORTANT: design document is available at request, contains most definitions that are and will be incorporated in the code.

## Run (Mac / Linux)
## in bash / terminal
python make_demo_dataset.py
python Surveyor.py
python HasherPacker.py

## Notes / limitations (by design)

- No Coordinator yet (manual order)
- No SQLite manifest yet (later)
- Audit log is not tamper‑evident yet
- Configuration is still hardcoded

