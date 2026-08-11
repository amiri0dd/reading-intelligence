from pathlib import Path


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CONFIG_DIR = PROJECT_ROOT / "config"

SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
TYPED_NOTES_DIR = PROJECT_ROOT / "typed_notes"
PROCESSED_DIR = PROJECT_ROOT / "processed"
VAULT_DIR = PROJECT_ROOT / "vault"

BOOKS_CSV = CONFIG_DIR / "books.csv"
CHAPTER_ALIASES_CSV = CONFIG_DIR / "chapter_aliases.csv"
CONCEPTS_CSV = CONFIG_DIR / "concepts.csv"

DEFAULT_TYPED_NOTES_FILE = (
    TYPED_NOTES_DIR / "quote_analysis.docx"
)

CONNECTIONS_JSON = (
    PROCESSED_DIR / "connections.json"
)

TYPED_JSON_DIR = (
    PROCESSED_DIR / "typed_notes"
)

BOOKS_VAULT_DIR = (
    VAULT_DIR / "Books"
)

PASSAGES_VAULT_DIR = (
    VAULT_DIR / "Passages"
)

CONCEPTS_VAULT_DIR = (
    VAULT_DIR / "Concepts"
)

READING_NOTES_VAULT_DIR = (
    VAULT_DIR / "Reading Notes"
)

ATTACHMENTS_VAULT_DIR = (
    VAULT_DIR / "Attachments"
)