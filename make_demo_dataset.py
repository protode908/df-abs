# make_demo_dataset.py (DFABS v0.1)
# Creates a small folder tree with a few files for demo/testing.

from pathlib import Path

BASE = Path(__file__).parent
DEMO = BASE / "demo_case_data"

def main():
    DEMO.mkdir(parents=True, exist_ok=True)
    (DEMO / "docs").mkdir(exist_ok=True)
    (DEMO / "misc").mkdir(exist_ok=True)

    (DEMO / "docs" / "note1.txt").write_text("demo evidence file 1\n", encoding="utf-8")
    (DEMO / "docs" / "note2.txt").write_text("demo evidence file 2\nkeyword: forensic\n", encoding="utf-8")
    (DEMO / "misc" / "image.jpg").write_bytes(b"\xff\xd8\xff\x00")  # not in allow-list

    # Optional: create a symlink to show policy blocking (might fail, symlink not properly working yet)
    try:
        link_path = DEMO / "docs" / "symlink_to_note1.txt"
        if link_path.exists() or link_path.is_symlink():
            link_path.unlink()
        link_path.symlink_to(DEMO / "docs" / "note1.txt")
    except Exception:
        pass

    print(f"Demo dataset created at: {DEMO}")

if __name__ == "__main__":
    main()
