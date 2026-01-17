# Surveyor.py (DFABS v0.4 , submission version)
#
# ROLE
# - Discover in-scope files within specified roots.
#
# WHY THE BOUNDARIES EXIST
# In a forensic-style workflow a tight scope is needed:
# - allow-listed roots (stay within evidence folders)
# - allow-listed extensions (reduce extensions)
# - max file size / max file count (allows limits on size/amount of files when needed), its not strictly related to the forensic action but for a PoC is very useful at this stage

import csv
import os
import sys
from pathlib import Path

from common import ensure_dir, read_json, write_json, make_message, append_runlog


def run(config: dict, base_dir: Path) -> bool:
    bus = base_dir / config["bus_dir"]
    out = base_dir / config["output_dir"]
    ensure_dir(bus)
    ensure_dir(out)

    case_id = config["case_id"]
    log_path = out / f"runlog_{case_id}.jsonl"

    # The Coordinator writes a TaskRequest message. Surveyor reads it.
    # “agents reacting to messages”, not just reading local config.
    task_path = bus / "00_task_request.json"
    task_cfg = {}
    if task_path.exists():
        try:
            task_cfg = read_json(task_path).get("content", {})
        except Exception:
            task_cfg = {}

    allowed_roots = task_cfg.get("allowed_roots", config["allowed_roots"])
    allowed_ext = [e.lower() for e in task_cfg.get("allowed_extensions", config["allowed_extensions"])]
    max_size = int(task_cfg.get("max_file_size_bytes", config["max_file_size_bytes"]))
    max_files = int(task_cfg.get("max_files", config["max_files"]))

    discovered = []
    deviations = []

    for root_rel in allowed_roots:
        root = (base_dir / root_rel)
        if not root.exists():
            deviations.append({"path": str(root), "reason": "root_missing"})
            continue

        for dirpath, _, filenames in os.walk(root, followlinks=False):
            for fn in filenames:
                p = Path(dirpath) / fn


                if p.suffix.lower() not in allowed_ext:
                    continue

                try:
                    st = p.stat()
                except Exception as e:
                    deviations.append({"path": str(p), "reason": f"stat_failed:{e}"})
                    continue

                if st.st_size > max_size:
                    deviations.append({"path": str(p), "reason": "size_limit"})
                    continue

                # Keep paths predictable for reporting.
                abs_path = str(p.resolve())
                rel_path = os.path.relpath(abs_path, str(root.resolve()))
                root_name = root.resolve().name

                discovered.append(
                    {
                        "path": abs_path,
                        "root": str(root.resolve()),
                        "root_name": root_name,
                        "rel_path": rel_path,
                        "ext": p.suffix.lower(),
                        "size": st.st_size,
                    }
                )

                if len(discovered) >= max_files:
                    deviations.append({"path": str(root), "reason": "max_files_reached"})
                    break
            if len(discovered) >= max_files:
                break

    # Write discovery CSV as a quick human-readable artefact, audit useful.
    discovery_csv = out / f"discovery_{case_id}.csv"
    with discovery_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "root", "root_name", "rel_path", "ext", "size"])
        w.writeheader()
        w.writerows(discovered)

    # Write message for next agent.
    msg = make_message(
        sender="Surveyor",
        receiver="HasherPacker",
        msg_type="DiscoveryReport",
        conversation_id=case_id,
        content={"files": discovered, "deviations": deviations},
        performative="INFORM",
    )
    msg_path = bus / "10_discovery_report.json"
    write_json(msg_path, msg)

    append_runlog(log_path, "Surveyor", "DISCOVERY", {"files": len(discovered), "deviations": len(deviations)})

    print(f"Surveyor: files={len(discovered)} deviations={len(deviations)}")
    print(f"- {discovery_csv}")
    print(f"- {msg_path}")
    return True


def main():
    base = Path(__file__).parent
    cfg_path = base / "config.json"
    if len(sys.argv) == 2:
        cfg_path = Path(sys.argv[1])

    config = read_json(cfg_path)
    run(config, base)


if __name__ == "__main__":
    main()
