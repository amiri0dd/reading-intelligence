from pathlib import Path
import json
import re

from src.analysis.theme_extractor import extract_themes
from src.ingestion.typed_notes_importer import parse_typed_document


VAULT_PATH = Path("vault")
PROCESSED_PATH = Path("processed")

BOOKS_DIR = VAULT_PATH / "Books"
PASSAGES_DIR = VAULT_PATH / "Passages"
READING_NOTES_DIR = VAULT_PATH / "Reading Notes"

TYPED_JSON_DIR = PROCESSED_PATH / "typed_notes"


def sanitize_filename(name: str) -> str:
    """
    Make a string safe for use as a Windows filename.
    """

    name = re.sub(r'[<>:"/\\|?*]', "-", name)
    name = re.sub(r"\s+", " ", name)

    return name.strip()


def ensure_directories() -> None:
    """
    Create output directories if they do not already exist.
    """

    for directory in [
        BOOKS_DIR,
        PASSAGES_DIR,
        READING_NOTES_DIR,
        TYPED_JSON_DIR,
    ]:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )


def add_themes_to_records(
    records: list[dict],
) -> list[dict]:
    """
    Run the existing deterministic concept extractor
    against each typed record.
    """

    enriched_records = []

    for record in records:
        enriched = dict(record)

        enriched["themes"] = extract_themes(
            record["text"]
        )

        enriched_records.append(
            enriched
        )

    return enriched_records


def export_records_as_json(
    records: list[dict],
) -> None:
    """
    Save each structured typed record as its own JSON file.
    """

    for record in records:
        filename = (
            sanitize_filename(
                record["record_id"]
            )
            + ".json"
        )

        output_path = (
            TYPED_JSON_DIR / filename
        )

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                record,
                file,
                indent=2,
                ensure_ascii=False,
            )


def concept_links(
    record: dict,
) -> list[str]:
    """
    Convert extracted themes into Obsidian concept links.
    """

    links = []

    for theme in record.get(
        "themes",
        [],
    ):
        concept_name = theme.get(
            "concept_name"
        )

        if concept_name:
            links.append(
                f"[[{concept_name}]]"
            )

    return sorted(
        set(links)
    )


def passage_note_filename(
    record: dict,
) -> str:
    """
    Build a stable passage-note filename.
    """

    title = sanitize_filename(
        record["book_title"]
    )

    record_id = sanitize_filename(
        record["record_id"]
    )

    return (
        f"{title} - {record_id}.md"
    )


def export_book_quote(
    record: dict,
) -> str:
    """
    Export one book quotation as an individual Passage note.

    Returns the note filename for backlinking.
    """

    filename = passage_note_filename(
        record
    )

    output_path = (
        PASSAGES_DIR / filename
    )

    book_title = record["book_title"]
    author = record["author"]

    book_note_name = sanitize_filename(
        book_title
    )

    themes = concept_links(
        record
    )

    theme_text = (
        "\n".join(
            f"- {theme}"
            for theme in themes
        )
        if themes
        else "- None detected"
    )

    content = f"""---
type: passage
record_id: "{record['record_id']}"
book_id: "{record['book_id']}"
book: "{book_title}"
author: "{author}"
source_type: typed_document
content_type: book_quote
provenance: book
---

# {book_title} - Passage

## Source

- Book: [[{book_note_name}|{book_title}]]
- Author: {author}
- Record ID: `{record['record_id']}`
- Source type: Typed document

## Passage

{record['text']}

## My Note

> Why did this passage stand out to me?

## Themes

{theme_text}

## Connections

"""

    output_path.write_text(
        content,
        encoding="utf-8",
    )

    return filename


def group_records_by_book(
    records: list[dict],
) -> dict[str, list[dict]]:
    """
    Group records by book_id.
    """

    grouped = {}

    for record in records:
        grouped.setdefault(
            record["book_id"],
            [],
        ).append(record)

    return grouped


def format_reading_record(
    record: dict,
) -> str:
    """
    Format a non-quote record for a Reading Notes page.
    """

    content_type = record[
        "content_type"
    ]

    heading_map = {
        "my_analysis": "My Analysis",
        "my_note": "My Note",
        "external_commentary": "External Commentary",
        "key_takeaways": "Key Takeaways",
        "entities_and_keywords": "Entities and Keywords",
    }

    heading = heading_map.get(
        content_type,
        content_type.replace(
            "_",
            " ",
        ).title(),
    )

    lines = [
        f"## {heading}",
        "",
    ]

    if (
        content_type
        == "external_commentary"
        and record.get("stance")
    ):
        lines.append(
            f"**Stance:** "
            f"{record['stance'].title()}"
        )

        lines.append("")

    lines.extend(
        [
            f"**Record ID:** "
            f"`{record['record_id']}`",
            "",
            record["text"],
            "",
        ]
    )

    themes = concept_links(
        record
    )

    if themes:
        lines.append(
            "**Concepts:** "
            + ", ".join(themes)
        )

        lines.append("")

    return "\n".join(lines)


def export_reading_notes(
    book_records: list[dict],
) -> str | None:
    """
    Export all non-quote records for a book into
    one Reading Notes page.
    """

    non_quotes = [
        record
        for record in book_records
        if record["content_type"]
        != "book_quote"
    ]

    if not non_quotes:
        return None

    first_record = book_records[0]

    book_title = first_record[
        "book_title"
    ]

    author = first_record[
        "author"
    ]

    book_note_name = sanitize_filename(
        book_title
    )

    filename = (
        sanitize_filename(
            f"{book_title} - Reading Notes"
        )
        + ".md"
    )

    output_path = (
        READING_NOTES_DIR
        / filename
    )

    sections = []

    for record in non_quotes:
        sections.append(
            format_reading_record(
                record
            )
        )

    body = "\n\n".join(
        sections
    )

    content = f"""---
type: reading_notes
book_id: "{first_record['book_id']}"
book: "{book_title}"
author: "{author}"
source_type: typed_document
---

# {book_title} - Reading Notes

## Book

[[{book_note_name}|{book_title}]]

## Notes and Commentary

{body}
"""

    output_path.write_text(
        content,
        encoding="utf-8",
    )

    return filename


def export_book_page(
    book_records: list[dict],
    passage_files: list[str],
    reading_notes_file: str | None,
) -> None:
    """
    Create or replace the Book page for a typed-notes book.
    """

    first_record = book_records[0]

    book_title = first_record[
        "book_title"
    ]

    author = first_record[
        "author"
    ]

    book_id = first_record[
        "book_id"
    ]

    filename = (
        sanitize_filename(
            book_title
        )
        + ".md"
    )

    output_path = (
        BOOKS_DIR / filename
    )

    passage_lines = []

    for passage_file in passage_files:
        note_name = Path(
            passage_file
        ).stem

        passage_lines.append(
            f"- [[{note_name}]]"
        )

    if passage_lines:
        passages_text = "\n".join(
            passage_lines
        )
    else:
        passages_text = (
            "- No saved passages yet."
        )

    if reading_notes_file:
        reading_note_name = Path(
            reading_notes_file
        ).stem

        reading_notes_text = (
            f"[[{reading_note_name}]]"
        )
    else:
        reading_notes_text = (
            "No reading notes yet."
        )

    content = f"""---
type: book
book_id: "{book_id}"
title: "{book_title}"
author: "{author}"
source_type: typed_document
---

# {book_title}

**Author:** {author}

**Book ID:** `{book_id}`

## Reading Notes

{reading_notes_text}

## Saved Passages

{passages_text}

## Recurring Themes

## Book-Level Notes

## Synthesis

"""

    output_path.write_text(
        content,
        encoding="utf-8",
    )


def export_typed_notes_to_obsidian(
    docx_path: str = (
        "typed_notes/quote_analysis.docx"
    ),
) -> None:
    """
    Main typed-notes export pipeline.
    """

    ensure_directories()

    print()
    print("=" * 70)
    print("TYPED NOTES → OBSIDIAN")
    print("=" * 70)

    records = parse_typed_document(
        docx_path
    )

    records = add_themes_to_records(
        records
    )

    export_records_as_json(
        records
    )

    books = group_records_by_book(
        records
    )

    total_passages = 0
    total_reading_notes = 0

    for book_id, book_records in books.items():

        passage_files = []

        for record in book_records:
            if (
                record["content_type"]
                == "book_quote"
            ):
                filename = export_book_quote(
                    record
                )

                passage_files.append(
                    filename
                )

                total_passages += 1

        reading_notes_file = (
            export_reading_notes(
                book_records
            )
        )

        if reading_notes_file:
            total_reading_notes += 1

        export_book_page(
            book_records,
            passage_files,
            reading_notes_file,
        )

        print(
            f"{book_id} | "
            f"{book_records[0]['book_title']} | "
            f"{len(passage_files)} passages"
        )

    print()
    print("=" * 70)
    print("EXPORT COMPLETE")
    print("=" * 70)

    print(
        f"Structured records: "
        f"{len(records)}"
    )

    print(
        f"Passage notes: "
        f"{total_passages}"
    )

    print(
        f"Reading Notes pages: "
        f"{total_reading_notes}"
    )

    print(
        f"Books exported: "
        f"{len(books)}"
    )

    print()
    print(
        "Open the vault in Obsidian "
        "to review the results."
    )


if __name__ == "__main__":
    export_typed_notes_to_obsidian()