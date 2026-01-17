# Scribe.py (DFABS v0.4 , submission version)
#
# ROLE
# - Produce a simple report CSV
#
# Design notes:
# - CSV is chosen because it is universal for quick human inspection, audits, etc.
# - The report doubles as a “hash manifest” for this proof-of-concept.
# 
# - Demonstrates complete workflow core functionality of DFABS as per design document DFABS Group D.

import csv
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

    hash_path = bus / "20_hash_result.json"
    if not hash_path.exists():
        print("Scribe ERROR: missing hash result message (run Coordinator first).")
        return False

    msg = read_json(hash_path)
    files = msg.get("content", {}).get("files", [])

    report_csv = out / f"report_{case_id}.csv"
    with report_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "ext", "size", "sha256", "arcname"])
        w.writeheader()
        for r in files:
            w.writerow(
                {
                    "path": r.get("path", ""),
                    "ext": r.get("ext", ""),
                    "size": r.get("size", ""),
                    "sha256": r.get("sha256", ""),
                    "arcname": r.get("arcname", ""),
                }
            )

    done = make_message(
        sender="Scribe",
        receiver="Coordinator",
        msg_type="ReportGenerated",
        conversation_id=case_id,
        content={"report_csv": str(report_csv), "rows": len(files)},
        performative="INFORM",
    )
    done_path = bus / "30_report_generated.json"
    write_json(done_path, done)

    append_runlog(log_path, "Scribe", "REPORT", {"rows": len(files), "report": report_csv.name})

    print(f"Scribe: rows={len(files)}")
    print(f"- {report_csv}")
    print(f"- {done_path}")
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
