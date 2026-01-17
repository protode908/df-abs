from pathlib import Path

import common
import Surveyor
import HasherPacker
import Scribe


def _base_config() -> dict:
    return {
        "case_id": "UT_CASE",
        "bus_dir": "bus",
        "output_dir": "output",
        "allowed_roots": ["evidence"],
        "allowed_extensions": [".txt"],
        "max_file_size_bytes": 100,
        "max_files": 100,
    }


def test_sha256_repeatable(tmp_path: Path):
    p = tmp_path / "x.txt"
    p.write_text("hello", encoding="utf-8")
    assert common.sha256_file(p) == common.sha256_file(p)


def test_surveyor_enforces_size_limit(tmp_path: Path):
    cfg = _base_config()
    base = tmp_path

    ev = base / "evidence"
    (ev / "docs").mkdir(parents=True)

    (ev / "docs" / "ok.txt").write_text("small", encoding="utf-8")
    (ev / "docs" / "big.txt").write_text("X" * 5000, encoding="utf-8")

    assert Surveyor.run(cfg, base) is True

    msg = common.read_json(base / "bus" / "10_discovery_report.json")
    files = msg.get("content", {}).get("files", [])
    devs = msg.get("content", {}).get("deviations", [])

    names = {Path(f["path"]).name for f in files}
    assert "ok.txt" in names
    assert "big.txt" not in names
    assert any(d.get("reason") == "size_limit" for d in devs)


def test_hasherpacker_requires_discovery_message(tmp_path: Path, capsys):
    cfg = _base_config()
    base = tmp_path
    (base / "bus").mkdir(parents=True, exist_ok=True)
    (base / "output").mkdir(parents=True, exist_ok=True)

    assert HasherPacker.run(cfg, base) is False
    out = capsys.readouterr().out.lower()
    assert "missing discovery" in out and "message" in out


def test_scribe_requires_hash_message(tmp_path: Path, capsys):
    cfg = _base_config()
    base = tmp_path
    (base / "bus").mkdir(parents=True, exist_ok=True)
    (base / "output").mkdir(parents=True, exist_ok=True)

    assert Scribe.run(cfg, base) is False
    out = capsys.readouterr().out.lower()
    assert "missing hash" in out and "message" in out
