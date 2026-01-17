# common.py (DFABS v0.2)
#
# Small common helpers so the agent scripts stay crisp to their intenttions and objectives, shared functions here.
# This is not a framework, only "my" version of shared functions for easy programming.

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

ONTOLOGY = "DFABS-Ontology"
PROTOCOL = "fipa-acl-lite"


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def make_message(sender: str, receiver: str, msg_type: str, conversation_id: str, content: dict, performative: str = "INFORM"):
    # Minimal “FIPA‑ACL‑lite” communication system.
    return {
        "protocol": PROTOCOL,
        "ontology": ONTOLOGY,
        "performative": performative,
        "sender": sender,
        "receiver": receiver,
        "type": msg_type,
        "conversation_id": conversation_id,
        "timestamp": utc_now(),
        "content": content,
    }


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
