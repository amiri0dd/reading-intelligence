import csv
from pathlib import Path

from docx import Document

from src.settings import (
    BOOKS_CSV,
    DEFAULT_TYPED_NOTES_FILE,
)


SECTION_HEADINGS = {
    "quote": "book_quote",
    "my analysis": "my_analysis",
    "my note": "my_note",
    "external commentary": "external_commentary",
    "key takeaways": "key_takeaways",
    "entities and keywords": "entities_and_keywords",
    "keywords": "entities_and_keywords",
}


def normalize_heading(text: str) -> str:
    """
    Normalize book and section headings.

    Examples:
        # Hayek's Bastards
        ## QUOTE
    """

    text = text.strip()

    # Remove Markdown-style heading markers.
    text = text.lstrip("#").strip()

    # Normalize curly apostrophes.
    text = text.replace("’", "'")

    # Normalize capitalization and whitespace.
    return " ".join(
        text.casefold().split()
    )


def clean_text(text: str) -> str:
    """
    Normalize whitespace without altering legitimate
    punctuation or hyphenation.
    """

    return " ".join(
        text.split()
    ).strip()


def load_typed_book_catalogue(
    books_path: Path = BOOKS_CSV,
) -> dict[str, dict]:
    """
    Load books.csv and create a title-based lookup for
    books that may appear in typed reading notes.
    """

    if not books_path.exists():
        raise FileNotFoundError(
            f"Could not find books catalogue: "
            f"{books_path}"
        )

    catalogue = {}

    with books_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        required_columns = {
            "book_id",
            "title",
            "author",
        }

        if reader.fieldnames is None:
            raise ValueError(
                "books.csv has no header row."
            )

        missing = (
            required_columns
            - set(reader.fieldnames)
        )

        if missing:
            raise ValueError(
                "books.csv is missing columns: "
                + ", ".join(sorted(missing))
            )

        for row in reader:
            book_id = (
                row.get("book_id", "")
                .strip()
            )

            title = (
                row.get("title", "")
                .strip()
            )

            author = (
                row.get("author", "")
                .strip()
            )

            if not book_id or not title:
                continue

            normalized_title = (
                normalize_heading(title)
            )

            catalogue[normalized_title] = {
                "book_id": book_id,
                "title": title,
                "author": author,
            }

    return catalogue


def read_docx_paragraphs(
    docx_path: str | Path,
) -> list[str]:
    """
    Read all non-empty paragraphs from a DOCX file.
    """

    path = Path(docx_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Could not find DOCX file: {path}"
        )

    document = Document(path)

    return [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]


def detect_book_heading(
    text: str,
    book_catalogue: dict[str, dict],
) -> dict | None:
    """
    Return book metadata if the paragraph matches
    a title in books.csv.
    """

    normalized = normalize_heading(text)

    return book_catalogue.get(
        normalized
    )


def detect_section_heading(
    text: str,
) -> str | None:
    """
    Identify explicit typed-note section labels.
    """

    normalized = normalize_heading(text)

    return SECTION_HEADINGS.get(
        normalized
    )


def parse_stance(
    text: str,
) -> str | None:
    """
    Parse optional metadata such as:

        Stance: critical
    """

    cleaned = clean_text(text)

    if not cleaned.casefold().startswith(
        "stance:"
    ):
        return None

    _, value = cleaned.split(
        ":",
        1,
    )

    value = value.strip().casefold()

    return value or None


def build_record(
    book: dict,
    content_type: str,
    paragraphs: list[str],
    record_number: int,
) -> dict | None:
    """
    Convert one explicitly marked section into
    a structured reading record.
    """

    cleaned_paragraphs = [
        clean_text(paragraph)
        for paragraph in paragraphs
        if clean_text(paragraph)
    ]

    if not cleaned_paragraphs:
        return None

    stance = None

    if (
        content_type
        == "external_commentary"
    ):
        possible_stance = parse_stance(
            cleaned_paragraphs[0]
        )

        if possible_stance:
            stance = possible_stance
            cleaned_paragraphs = (
                cleaned_paragraphs[1:]
            )

    if not cleaned_paragraphs:
        return None

    if (
        content_type
        == "entities_and_keywords"
    ):
        text = "\n".join(
            cleaned_paragraphs
        )

    else:
        text = "\n\n".join(
            cleaned_paragraphs
        )

    provenance_map = {
        "book_quote": "book",
        "my_analysis": "my_analysis",
        "my_note": "my_note",
        "external_commentary":
            "external_commentary",
        "key_takeaways": "my_analysis",
        "entities_and_keywords":
            "unknown",
    }

    record_id = (
        f"{book['book_id']}-T"
        f"{record_number:03d}"
    )

    return {
        "record_id": record_id,
        "source_kind": "typed_document",
        "source_type": "typed_document",
        "book_id": book["book_id"],
        "book_title": book["title"],
        "author": book["author"],
        "chapter": "",
        "content_type": content_type,
        "provenance": (
            provenance_map.get(
                content_type,
                "unknown",
            )
        ),
        "stance": stance,
        "text": text,
    }


def parse_typed_document(
    docx_path: str | Path = (
        DEFAULT_TYPED_NOTES_FILE
    ),
) -> list[dict]:
    """
    Parse a structured typed-notes DOCX.

    Expected structure:

        # Book Title

        ## QUOTE
        ...

        ## MY ANALYSIS
        ...

        ## EXTERNAL COMMENTARY
        ...
    """

    book_catalogue = (
        load_typed_book_catalogue()
    )

    paragraphs = read_docx_paragraphs(
        docx_path
    )

    records = []

    current_book = None
    current_content_type = None
    current_content = []

    book_record_counts = {}

    def flush_current_record():
        nonlocal current_content

        if (
            current_book is None
            or current_content_type is None
            or not current_content
        ):
            current_content = []
            return

        book_id = current_book[
            "book_id"
        ]

        next_number = (
            book_record_counts.get(
                book_id,
                0,
            )
            + 1
        )

        record = build_record(
            current_book,
            current_content_type,
            current_content,
            next_number,
        )

        if record:
            records.append(record)

            book_record_counts[
                book_id
            ] = next_number

        current_content = []

    for paragraph in paragraphs:

        book_match = (
            detect_book_heading(
                paragraph,
                book_catalogue,
            )
        )

        if book_match:
            flush_current_record()

            current_book = book_match
            current_content_type = None
            current_content = []

            continue

        section_match = (
            detect_section_heading(
                paragraph
            )
        )

        if section_match:
            flush_current_record()

            current_content_type = (
                section_match
            )

            current_content = []

            continue

        if (
            current_book is not None
            and current_content_type
            is not None
        ):
            current_content.append(
                paragraph
            )

    flush_current_record()

    return records


def summarize_records(
    records: list[dict],
) -> None:
    """
    Print record counts by book and type.
    """

    print()
    print("=" * 70)
    print("STRUCTURED TYPED RECORDS")
    print("=" * 70)

    counts = {}

    for record in records:
        key = (
            record["book_id"],
            record["content_type"],
        )

        counts[key] = (
            counts.get(key, 0) + 1
        )

    for (
        book_id,
        content_type,
    ), count in sorted(
        counts.items()
    ):
        print(
            f"{book_id} | "
            f"{content_type} | "
            f"{count}"
        )

    print()
    print(
        f"Total structured records: "
        f"{len(records)}"
    )


if __name__ == "__main__":
    records = parse_typed_document()

    summarize_records(records)