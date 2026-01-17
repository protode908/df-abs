# DFABS v0.2
# HasherPacker Agent (Hash + ZIP)
#
# PURPOSE (core design step: HASH + ARCHIVE in zip)
# - Reads Surveyor discovery message
# - Hashes each file with SHA‑256
# - Writes a ZIP archive
#
# WHY SHA‑256
# - Broad compatibility and widely used in forensics. Remember, design document is available which contains many of these defintions.
# General

import csv
import zipfile
from pathlib import Path

from common import read_json, write_json, make_message, sha256_file

BUS_DIR = "bus"
OUT_DIR = "output"


def main():
    base = Path(__file__).parent
    bus = base / BUS_DIR
    out = base / OUT_DIR
    bus.mkdir(exist_ok=True)
    out.mkdir(exist_ok=True)

    discovery_path = bus / "10_discovery_report.json"
    if not discovery_path.exists():
        print("ERROR: missing discovery message. Run Surveyor.py first.")
        return

    discovery = read_json(discovery_path)
    case_id = discovery.get("conversation_id", "CASE-UNKNOWN")
    files = discovery.get("content", {}).get("files", [])

    zip_path = out / f"evidence_{case_id}.zip"
    manifest_csv = out / f"hash_manifest_{case_id}.csv"

    results = []

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for item in files:
            p = Path(item["path"])
            if not p.exists():
                continue

            digest = sha256_file(p)

            # Keep archive paths simple
            arcname = p.name
            z.write(p, arcname=arcname)

            results.append(
                {
                    "path": str(p),
                    "sha256": digest,
                    "size": item.get("size", ""),
                    "ext": item.get("ext", ""),
                }
            )

    # Evidence output (hash CSV)
    with manifest_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "ext", "size", "sha256"])
        w.writeheader()
        w.writerows(results)

    # Agent message to next stage, no other agent yet to pull it but testing functions alreay.
    msg = make_message(
        sender="HasherPacker",
        receiver="Coordinator",
        msg_type="HashResult",
        conversation_id=case_id,
        content={"files": results, "zip_path": str(zip_path), "manifest_csv": str(manifest_csv)},
    )
    msg_path = bus / "20_hash_result.json"
    write_json(msg_path, msg)

    print("HasherPacker v0.2 finished.")
    print(f"- Hashed files:      {len(results)}")
    print(f"- ZIP:              {zip_path}")
    print(f"- Hash manifest CSV: {manifest_csv}")
    print(f"- Message:          {msg_path}")


if __name__ == "__main__":
    main()
