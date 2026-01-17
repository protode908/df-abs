# make_demo_dataset.py (DFABS v0.4 , submission version)
#
# Creates a small folder tree with a file "truth-set" for the submission, in this way we create repeatable evidence to showcase, test, demos, etc.
# This makes it easy to show evidence of execution.

from pathlib import Path

BASE = Path(__file__).parent
DEMO = BASE / "demo_case_data"

def main():
    DEMO.mkdir(parents=True, exist_ok=True)
    (DEMO / "docs").mkdir(exist_ok=True)
    (DEMO / "other").mkdir(exist_ok=True)
    (DEMO / "misc").mkdir(exist_ok=True)

    (DEMO / "docs" / "note1.txt").write_text("demo evidence file 1\n", encoding="utf-8")
    (DEMO / "docs" / "note2.txt").write_text("demo evidence file 2\nkeyword: forensic\n", encoding="utf-8")

    # Duplicate filename in a different folder to exercise ZIP name-collision handling
    (DEMO / "other" / "note1.txt").write_text("same name, different folder\n", encoding="utf-8")

    # A file that should be ignored (extension not allow-listed)
    (DEMO / "misc" / "image.jpg").write_bytes(b"\xff\xd8\xff\x00")

    print(f"Demo dataset created at: {DEMO}")

if __name__ == "__main__":
    main()
