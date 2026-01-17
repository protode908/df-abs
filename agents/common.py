# common.py (DFABS v0.4 – submission version)
#
# This module is intentionally small.
# This is not a framework, rather a small set of functions shared by all agents mainly for agent communication.
# 
# Design choices:
# - JSON files are used as messages to keep agent communication visible for demos.
# - SHA-256 is used for file integrity because it is widely recognized and simple to explain. This is also in line with the original DFABS design document Group D submission.
# - The run log is plain JSON Lines (jsonl) so it is easy to capture as evidence.
#
# Out of scope in this build, designed originally but not included due to constrains, plan for next versions:
# - tamper-evident log
# - schema validation frameworks for messages
# - network
# Design notes:
# - Demonstrates complete workflow core functionality of DFABS as per design document DFABS Group D. Originally as per agent design there was no common functions, although this is not really an agent related design choice.

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

PROTOCOL = "dfabs-acl-lite"
ONTOLOGY = "DFABS-Ontology"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: dict):
    ensure_dir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def make_message(sender: str, receiver: str, msg_type: str, conversation_id: str, content: dict, performative: str = "INFORM") -> dict:
    # Minimal envelope inspired by FIPA ACL terminology.
    # The goal is to make inter-agent communication explicit and reviewable, sort of log based. pseudo-bus.
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


def sha256_file(path: Path) -> str:
    # PoC assumption: evidence files are small (enforced by max_file_size_bytes).
    # Reading the whole file keeps the code simple.
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def append_runlog(log_path: Path, agent: str, action: str, details: dict):
    # Plain JSONL for evidence, reproducibility, checking and test.
    record = {"ts": utc_now(), "agent": agent, "action": action, "details": details}
    ensure_dir(log_path.parent)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
