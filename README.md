# DFABS (Digital Forensic Agent-Based System) – v0.4 (Proof of Concept for university project - MSc AI programme, Inteligent Agents module, Individual project)
## What ? is this
DFABS is a small agent-based forensic proof-of-concept written in Python. It demonstrates a simple workflow where multiple agents cooperate (via file messages) to:
1. **Discover** in-scope files (Surveyor)2. **Hash + preserve** the discovered files into a ZIP archive (HasherPacker)3. **Generate a report** (Scribe)4. **Orchestrate** the process and keep an execution log (Coordinator)
It is based on the FABS design document, which stipulates a Hybrid BDI agent based system with one BDI coordinator and 3 reactive agents. This version is deliberately  is simple, yet functional, showcasing and proving key core workflow functionality. It is based on the Group D ABS design document to which the author of this DFABS is a member.
---
---

## 2. Project Structure

Typical structure (key items):

- `agents/`
  - `Coordinator.py` – orchestration entrypoint: calls the other agents in order
  - `Surveyor.py` – discovers eligible files according to constraints
  - `HasherPacker.py` – hashes discovered files and produces an evidence ZIP
  - `Scribe.py` – writes the final CSV report from the hash results
  - `common.py` – shared utilities (JSON I/O, hashing helpers, directory helpers, runlog helper)
  - `config.json` – example configuration file
  - `test_dfabs_unit.py` – unit tests (pytest) **for the current submission layout**
- `requirements.txt` – Python dependencies needed for testing (pytest)

During execution, the code creates (or uses) the following folders **inside `agents/`**:

- `bus/` – file-based “messages” passed between agents
- `output/` – run outputs (CSV report, run log, evidence ZIP, etc.)

> Note: folder names can be configured via `config.json` (`bus_dir`, `output_dir`).

---

## 3. Requirements

- Python **3.x** (macOS/Linux commands shown with `python3`)
- `pip` (Python package installer)
- Optional but recommended: a venv virtual environment for clean installation

Check Python version:

```bash
python3 --version
```
Or

```bash
python --version
```

NOTE: depending on the installed version, OS and distribution, python can be called python or python3. So from now on regardless of the instructions below, you need to make sure how do you call your python interpreter in your OS and replace accordingly.
---

## 4. Installation

### 4.1 Run your normal python environment.

Python installation is OS and dsitro dependent, and pretty common. However, in MacOS best is to use home-brew or official python distribution. It is not officially distributed by Apple in a vendor provided package to the best of my knowledge. For Linux it depends not he distro package manager. 
Recommended: it is OS dependent, but on https://www.python.org/ you find the official source and installers.

### 4.2 Install dependencies

This submission uses `requirements.txt` for reproducibility:
Example in bash shell:

```bash
python3 -m pip install -r requirements.txt
```

Verify `pytest` is installed:

```bash
python3 -m pytest --version
```

---

## 5. Configuration (`config.json`)

The pipeline is configured using a JSON file. By default, `Coordinator.py` looks for:

- `agents/config.json`

You can also pass a custom config path:

```bash
python3 Coordinator.py /path/to/your_config.json
```

### 5.1 Config fields

A typical config contains:

- `case_id`  
  A unique ID used in filenames (runlog/report naming). This is user configured for now.
- `allowed_roots`  
  List of root folders (relative to `agents/`) that the Surveyor is allowed to scan.
- `allowed_extensions`  
  List of file extensions allowed for discovery (`.txt`, `.pdf`, etc.).
- `max_file_size_bytes`  
  Maximum size per file to include.
- `max_files`
  Maximum number of files.
- `bus_dir`  
  Folder name for the message bus (e.g., `bus`).
- `output_dir`
  Output folder name (e.g., `output`).

### 5.2 Important JSON note when customizing the config:

`config.json` **must have a valid JSON format**. JSON **does not allow trailing commas**

 Valid:

```json
"allowed_extensions": [".txt", ".pdf", ".doc"]
```

Invalid (trailing comma):

```json
"allowed_extensions": [".txt", ".pdf", ".doc",]
```

---

## 6. Running the workflow pipeline

### 6.1 Generate demo dataset

Generates a demo data set with folders and files for a forensic exercise.

From inside `agents/`:

```bash
cd agents
python3 make_demo_dataset.py
```

This creates the folder tree and a few files for discovery. Default config comes with that directory pre-configured.

### 6.2 Run Coordinator (main execution)

From inside `agents/`:

```bash
cd agents
python3 Coordinator.py
```

Or if you want an explicit config path, for example an alternative config for testing:

```bash
cd agents
python3 Coordinator.py config.json
```

### 6.3 Outputs

After a successful run, check:

- `agents/output/`  
  Contains reports, run log(s), and evidence artifacts
- `agents/bus/`  
  Contains the inter-agent message JSON files between agents

---

## 7. Testing (Unit Tests with pytest)

### 7.1 Location

The unit test file is located inside the agents folder:

- `agents/test_dfabs_unit.py`
- it allows imports like `import common` to work without extra packaging steps.

### 7.2 Install pytest

Pytest is listed in `requirements.txt`. Install with:

```bash
python3 -m pip install -r requirements.txt
```

### 7.3 Run the tests

Because the tests have execution within `agents/`, run pytest from that directory:

```bash
cd agents
python3 -m pytest -q
```

To run only the test file explicitly:

```bash
cd agents
python3 -m pytest -q test_dfabs_unit.py
```
Or directly run
```bash
pytest test_dfabs_unit.py
```

### 7.4 Expected output

Successful run:

- `N (tests) passed in Xs (seconds)`

If a test fails, pytest prints:
- the failing test name
- the assertion that failed
- a traceback to the offender line

### 7.5 Troubleshooting

#### A) `ModuleNotFoundError: No module named 'common'`

Cause:
- pytest was executed from a folder where Python cannot access `common.py`.

Fix:
- run from `agents/` directory as shown below:

```bash
cd agents
python3 -m pytest -q
```

#### B) `No module named pytest` / pytest not installed

Fix:

```bash
python3 -m pip install -r requirements.txt
```

---

## 8. Reproducibility

1. The repository includes:
   - source code under `agents/`
   - `requirements.txt` for test dependency installation
   - this `README.md` with explicit run/test commands

2. The recommended execution flow is:
   - create venv, install requirements (pytest), run pipeline, run tests

3. All paths in the commands are always relative:
   - project root (for environment setup)
   - `agents/` (for running the pipeline and tests)

---

## 9. Submission notes, summary:

- Install dependencies using `requirements.txt`
- Run unit tests with `python3 -m pytest -q` from `agents/`
- Execute the DFABS workflow by running `python3 Coordinator.py` from `agents/`


## 10. Design notes, limitations
This is a prototype and focused on core workflow functionality. A few originally designed where left for later versions, such as symlink block, SQLlite repo. Other more advanced functionality like network, SHA streaming, etc. where also left out and documented in the presentation appropiately.
This code is based on the mentioned design document for the DFABS Group D submission. If you are not an examineer or tutor looking at this code and README, feel free to request the design document and I will gladly shared as appropiate.
Assumptions that keeps the code simple:
- **Local execution only**: agents communicate by writing/reading files in `bus/`, which i build as a pseudo-bus messaging system, it emulates an equivalent version of FIPA-ACL which was part of the original design. Note: referred in the code as FIPA-ACL-LITE however note there is no such formal thing its an invention of my own in the sense of a homemade equivalency - **Trusted environment**: no encryption, authentication, or network security- **Small evidence set**: file size and amount is limited by config by default, and for demo purposes; hashing reads whole file content into memory (I tried more secure and better performing/scalable streaming but was too complex for a proof of concept, thus left out for now)- **Simple logging**: `runlog_*.jsonl` is an append-only execution record   (cryptographic tamper-evidence not implemented yet)
---
## References
- full academic compliance set of references is provided 1) in the original design document and 2) in the submission presentation as slide number 11.
Rational: list of references too long to include on a public README.