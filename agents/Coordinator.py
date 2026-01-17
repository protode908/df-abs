# Coordinator.py (DFABS v0.4, submission code)
#
# ROLE
# - Orchestrate the agent workflow in a strict order:
#     Surveyor -> HasherPacker -> Scribe
#
# WHY A COORDINATOR EXISTS
# - DFABS is based on a hybrid BDI agent architecture, being the coordinator the orchestration agent.
# - Ordering matters in forensic-style workflows (discover before hashing, etc.).
#
# The “agent communication” is intentionally visible:
# - Coordinator writes a TaskRequest message to bus/
# - Each agent reads/writes JSON messages to bus/
# Design notes:
# - Demonstrates complete workflow core functionality of DFABS as per design document DFABS Group D.

import sys
from pathlib import Path

import Surveyor
import HasherPacker
import Scribe

from common import ensure_dir, read_json, write_json, make_message, append_runlog


def wipe_bus(bus_dir: Path):
    # Keep demos repeatable
    if not bus_dir.exists():
        return
    for p in bus_dir.glob("*.json"):
        try:
            p.unlink()
        except Exception:
            pass


def main():
    base = Path(__file__).parent
    cfg_path = base / "config.json"
    if len(sys.argv) == 2:
        cfg_path = Path(sys.argv[1])

    config = read_json(cfg_path)

    bus = base / config["bus_dir"]
    out = base / config["output_dir"]
    ensure_dir(bus)
    ensure_dir(out)

    case_id = config["case_id"]
    log_path = out / f"runlog_{case_id}.jsonl"

    wipe_bus(bus)

    append_runlog(log_path, "Coordinator", "TASK_START", {"case_id": case_id})

    # Task request message: mirrors how an agent system can carry “intent” and constraints.
    task = make_message(
        sender="Coordinator",
        receiver="Surveyor",
        msg_type="TaskRequest",
        conversation_id=case_id,
        content={
            "allowed_roots": config["allowed_roots"],
            "allowed_extensions": config["allowed_extensions"],
            "max_file_size_bytes": config["max_file_size_bytes"],
            "max_files": config["max_files"],
        },
        performative="REQUEST",
    )
    write_json(bus / "00_task_request.json", task)

    print("Coordinator: DFABS run v0.4")
    print(f"- RunID: {case_id}")

    if not Surveyor.run(config, base):
        append_runlog(log_path, "Coordinator", "TASK_FAIL", {"stage": "Surveyor"})
        return

    if not HasherPacker.run(config, base):
        append_runlog(log_path, "Coordinator", "TASK_FAIL", {"stage": "HasherPacker"})
        return

    if not Scribe.run(config, base):
        append_runlog(log_path, "Coordinator", "TASK_FAIL", {"stage": "Scribe"})
        return

    append_runlog(log_path, "Coordinator", "TASK_END", {"case_id": case_id})

    print("Coordinator: finished OK (DFABS)")
    print(f"- Output folder: {out}")
    print(f"- Run log: {log_path}")


if __name__ == "__main__":
    main()
