# Reading Intelligence

Reading Intelligence is a local-first Python and Obsidian system for turning saved reading material into a structured personal knowledge base.

The system supports:

- Xteink X4 e-reader screenshots
- OCR-based passage extraction
- Book and chapter identification
- Structured typed reading notes
- Deterministic concept tagging
- Cross-book semantic similarity
- Obsidian Markdown export
- Preservation of source provenance

No paid APIs or generative-AI interpretation are required.

## Architecture

### Xteink workflow

BMP screenshot

→ OCR

→ book/chapter classification

→ structured JSON

→ concept extraction

→ Obsidian passage

### Typed-notes workflow

Structured DOCX

→ book detection

→ section parsing

→ structured JSON

→ concept extraction

→ Obsidian passages and reading notes

Both branches then feed into the same semantic cross-book linking system.

## Setup

Create and activate a Python virtual environment.

On Windows PowerShell:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
