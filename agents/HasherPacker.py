# HasherPacker.py (DFABS v0.4, submission code)
#
# ROLE
# - Agent that takes the forensic matching files (and under policy), computes a SHA fingerprints and archives it.
# - Compute SHA-256 hashes (integrity)
# - Create a ZIP preservation archive copy of each evidence file
#
# Design notes:
# - Demonstrates complete workflow core functionality of DFABS as per design document DFABS Group D.
# - ZIP is used because it is widely available and easy to demonstrate.
# - The ZIP entry names include relative paths to avoid name collisions.
# - No SQLlite in this version.

import sys
import zipfile
from pathlib import Path

from common import ensure_dir, read_json, write_json, make_message, sha256_file, append_runlog


def _zip_name(item: dict) -> str:
    # A realistic issue: different folders can contain the same filename.
    # Using <root>/<relative_path> keeps entries unique and preserves location context.
    root_name = item.get("root_name") or "root"
    rel_path = item.get("rel_path") or Path(item.get("path", "file")).name
    return f"{root_name}/{rel_path}".replace("\\", "/")


def run(config: dict, base_dir: Path) -> bool:
    bus = base_dir / config["bus_dir"]
    out = base_dir / config["output_dir"]
    ensure_dir(bus)
    ensure_dir(out)

    case_id = config["case_id"]
    log_path = out / f"runlog_{case_id}.jsonl"

    discovery_path = bus / "10_discovery_report.json"
    if not discovery_path.exists():
        print("HasherPacker ERROR: missing discovery message (run Coordinator first).")
        return False

    discovery = read_json(discovery_path)
    items = discovery.get("content", {}).get("files", [])

    zip_path = out / f"evidence_{case_id}.zip"

    results = []

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for it in items:
            p = Path(it["path"])
            if not p.exists():
                continue

            try:
                digest = sha256_file(p)
            except Exception as e:
                # Keep the PoC moving: log the failure and continue.
                results.append({"path": str(p), "sha256": "", "error": str(e)})
                continue

            arcname = _zip_name(it)
            z.write(p, arcname=arcname)

            results.append(
                {
                    "path": str(p),
                    "ext": it.get("ext", ""),
                    "size": it.get("size", 0),
                    "sha256": digest,
                    "arcname": arcname,
                }
            )

    msg = make_message(
        sender="HasherPacker",
        receiver="Scribe",
        msg_type="HashResult",
        conversation_id=case_id,
        content={"files": results, "zip_path": str(zip_path)},
        performative="INFORM",
    )
    msg_path = bus / "20_hash_result.json"
    write_json(msg_path, msg)

    append_runlog(log_path, "HasherPacker", "HASH_AND_ZIP", {"files": len(results), "zip": zip_path.name})

    print(f"HasherPacker: files={len(results)}")
    print(f"- {zip_path}")
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
