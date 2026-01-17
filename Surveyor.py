# DFABS v0.2
# Surveyor Agent (Discovery)
#
# Changes from v0.1:
# - Uses common.py shared functions
# - Still hardcodes config

import csv
import os
from pathlib import Path

from common import make_message, write_json

# ----------------------------
# HARD-CODED CONFIG (v0.2)
# ----------------------------
CASE_ID = "CASE-DEMO-001"
ALLOWED_ROOTS = ["demo_case_data"]
ALLOWED_EXTENSIONS = [".txt", ".pdf", ".doc", ".docx"]
MAX_FILE_SIZE_BYTES = 5_000_000
MAX_FILES = 200

BUS_DIR = "bus"
OUT_DIR = "output"


def is_under_root(resolved_path: Path, resolved_root: Path) -> bool:
    try:
        resolved_path.relative_to(resolved_root)
        return True
    except Exception:
        return False


def main():
    base = Path(__file__).parent
    bus = base / BUS_DIR
    out = base / OUT_DIR
    bus.mkdir(exist_ok=True)
    out.mkdir(exist_ok=True)

    discovered = []
    deviations = []

    for root_rel in ALLOWED_ROOTS:
        root = (base / root_rel).resolve()

        if not root.exists():
            deviations.append({"path": str(root), "reason": "root_missing"})
            continue

        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            for fn in filenames:
                p = Path(dirpath) / fn

                if p.is_symlink():
                    deviations.append({"path": str(p), "reason": "symlink_blocked"})
                    continue

                if p.suffix.lower() not in ALLOWED_EXTENSIONS:
                    continue

                try:
                    st = p.stat()
                except Exception as e:
                    deviations.append({"path": str(p), "reason": f"stat_failed:{e}"})
                    continue

                if st.st_size > MAX_FILE_SIZE_BYTES:
                    deviations.append({"path": str(p), "reason": "size_limit"})
                    continue

                rp = p.resolve()
                if not is_under_root(rp, root):
                    deviations.append({"path": str(rp), "reason": "out_of_scope"})
                    continue

                discovered.append({"path": str(rp), "root": str(root), "ext": p.suffix.lower(), "size": st.st_size})

                if len(discovered) >= MAX_FILES:
                    deviations.append({"path": str(root), "reason": "max_files_reached"})
                    break
            if len(discovered) >= MAX_FILES:
                break

    # Evidence output (CSV)
    csv_path = out / f"discovery_{CASE_ID}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "root", "ext", "size"])
        w.writeheader()
        w.writerows(discovered)

    # Agent message to next stage
    msg = make_message(
        sender="Surveyor",
        receiver="HasherPacker",
        msg_type="DiscoveryReport",
        conversation_id=CASE_ID,
        content={"files": discovered, "deviations": deviations},
    )
    msg_path = bus / "10_discovery_report.json"
    write_json(msg_path, msg)

    print("Surveyor v0.2 finished.")
    print(f"- Discovered files: {len(discovered)}")
    print(f"- CSV:              {csv_path}")
    print(f"- Message:          {msg_path}")


if __name__ == "__main__":
    main()
