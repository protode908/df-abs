# DFABS v0.1
# Surveyor Agent - file dicovery prototype
#
# PURPOSE (core workflow, design step 1: DISCOVER
# - run through allow‑listed roots and discover files matching allow‑listed extensions. (testing functionality)
# - Apply strict boundaries (for scope control):
#     * Only allow-listed roots
#     * No symlinks (in test, it does not work properly yet)
#     * Max file size, max files
#
# WHY THIS VERSION IS SMALL
# - This is an early prototype. It focuses only on very basic workflow functionality, but not yet on true agent design, i.e. eg.: undertstands scope, boundaries, runs, discover files; all under 
#  same agent. no coordination, no archival yet, no sql, etc. to better understand scope, request the scope design to the author (university MSc AI studies, module Inteligent Agents).
#   Already tests pseudo-bus message function as "FIPA-ACL-lite" (my invention, not really existant but as equivalency for experimentation purposes) communication system.
#
# OUTPUTS
# - output/discovery_<CASE>.csv
# - bus/10_discovery_report.json   (FIPA‑ACL‑lite message, simplified)

import csv
import json
import os
from pathlib import Path
from datetime import datetime, timezone

# ----------------------------
# HARD-CODED CONFIG (v0.1)
# ----------------------------
CASE_ID = "CASE-DEMO-001"
ALLOWED_ROOTS = ["demo_case_data"]        # relative to this script folder
ALLOWED_EXTENSIONS = [".txt", ".pdf", ".doc", ".docx"]
MAX_FILE_SIZE_BYTES = 5_000_000           # 5 MB
MAX_FILES = 200

BUS_DIR = "bus"
OUT_DIR = "output"


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def is_under_root(resolved_path: Path, resolved_root: Path) -> bool:
    # Simple path traversal control
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

                # Boundary: no symlinks (do not trust them in a basic prototype)
                if p.is_symlink():
                    deviations.append({"path": str(p), "reason": "symlink_blocked"})
                    continue

                # Boundary: file type allow-list
                if p.suffix.lower() not in ALLOWED_EXTENSIONS:
                    continue

                try:
                    st = p.stat()
                except Exception as e:
                    deviations.append({"path": str(p), "reason": f"stat_failed:{e}"})
                    continue

                # Boundary: size limit
                if st.st_size > MAX_FILE_SIZE_BYTES:
                    deviations.append({"path": str(p), "reason": "size_limit"})
                    continue

                rp = p.resolve()
                if not is_under_root(rp, root):
                    deviations.append({"path": str(rp), "reason": "out_of_scope"})
                    continue

                discovered.append(
                    {
                        "path": str(rp),
                        "ext": p.suffix.lower(),
                        "size": st.st_size,
                    }
                )

                if len(discovered) >= MAX_FILES:
                    deviations.append({"path": str(root), "reason": "max_files_reached"})
                    break
            if len(discovered) >= MAX_FILES:
                break

    # Write discovery CSV (simple evidence output)
    csv_path = out / f"discovery_{CASE_ID}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "ext", "size"])
        writer.writeheader()
        writer.writerows(discovered)

    # Write a simple “FIPA‑ACL‑lite” message (we keep it minimal in v0.1)
    msg = {
        "protocol": "fipa-acl-lite",
        "performative": "INFORM",
        "sender": "Surveyor",
        "receiver": "Coordinator",
        "type": "DiscoveryReport",
        "conversation_id": CASE_ID,
        "timestamp": utc_now(),
        "content": {"files": discovered, "deviations": deviations},
    }
    msg_path = bus / "10_discovery_report.json"
    msg_path.write_text(json.dumps(msg, indent=2), encoding="utf-8")

    print("Surveyor v0.1 finished.")
    print(f"- Discovered files: {len(discovered)}")
    print(f"- Deviations:       {len(deviations)}")
    print(f"- CSV:              {csv_path}")
    print(f"- Message:          {msg_path}")


if __name__ == "__main__":
    main()
