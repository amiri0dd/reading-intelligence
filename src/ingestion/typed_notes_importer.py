from pathlib import Path
from docx import Document


BOOK_HEADINGS = {
    "hayek's bastards": {
        "book_id": "B004",
        "title": "Hayek's Bastards",
        "author": "Quinn Slobodian",
    },
    "rise & fall of the neoliberal order": {
        "book_id": "B005",
        "title": "The Rise and Fall of the Neoliberal Order",
        "author": "Gary Gerstle",
    },
    "the rise and fall of the neoliberal order": {
        "book_id": "B005",
        "title": "The Rise and Fall of the Neoliberal Order",
        "author": "Gary Gerstle",
    },
    "the strange death of europe": {
        "book_id": "B006",
        "title": "The Strange Death of Europe",
        "author": "Douglas Murray",
    },
}


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
    """

    text = text.strip()

    text = text.lstrip("#").strip()

    text = text.replace("’", "'")

    return " ".join(
        text.casefold().split()
    )


def clean_text(text: str) -> str:
    """
    Clean whitespace and repair common line-wrap artifacts.
    """

    text = " ".join(text.split())

    # Repair split words caused by PDF/book copy formatting.
    text = text.replace("- ", "")

    return text.strip()


def read_docx_paragraphs(
    docx_path: str,
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

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return paragraphs


def detect_book_heading(
    text: str,
) -> dict | None:
    """
    Return book metadata if the paragraph is a book heading.
    """

    normalized = normalize_heading(text)

    return BOOK_HEADINGS.get(normalized)


def detect_section_heading(
    text: str,
) -> str | None:
    """
    Return normalized content type if paragraph is
    a recognized section heading.
    """

    normalized = normalize_heading(text)

    return SECTION_HEADINGS.get(normalized)


def parse_stance(
    text: str,
) -> str | None:
    """
    Detect optional stance metadata inside external commentary.
    """

    cleaned = clean_text(text)

    if not cleaned.casefold().startswith("stance:"):
        return None

    _, value = cleaned.split(":", 1)

    value = value.strip().casefold()

    if value in {
        "supportive",
        "critical",
        "mixed",
        "neutral",
    }:
        return value

    return value or None


def build_record(
    book: dict,
    content_type: str,
    paragraphs: list[str],
    record_number: int,
) -> dict | None:
    """
    Convert a section into one structured record.
    """

    if not paragraphs:
        return None

    cleaned_paragraphs = [
        clean_text(paragraph)
        for paragraph in paragraphs
        if clean_text(paragraph)
    ]

    if not cleaned_paragraphs:
        return None

    stance = None

    if content_type == "external_commentary":
        first_stance = parse_stance(
            cleaned_paragraphs[0]
        )

        if first_stance:
            stance = first_stance
            cleaned_paragraphs = cleaned_paragraphs[1:]

    if not cleaned_paragraphs:
        return None

    if content_type == "entities_and_keywords":
        text = "\n".join(cleaned_paragraphs)
    else:
        text = "\n\n".join(cleaned_paragraphs)

    provenance_map = {
        "book_quote": "book",
        "my_analysis": "my_analysis",
        "my_note": "my_note",
        "external_commentary": "external_commentary",
        "key_takeaways": "unknown",
        "entities_and_keywords": "unknown",
    }

    record_id = (
        f"{book['book_id']}-T"
        f"{record_number:03d}"
    )

    return {
        "record_id": record_id,
        "book_id": book["book_id"],
        "book_title": book["title"],
        "author": book["author"],
        "source_type": "typed_document",
        "content_type": content_type,
        "provenance": provenance_map.get(
            content_type,
            "unknown",
        ),
        "stance": stance,
        "text": text,
    }


def parse_typed_document(
    docx_path: str = "typed_notes/quote_analysis.docx",
) -> list[dict]:
    """
    Parse the structured DOCX into typed reading records.
    """

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

        book_id = current_book["book_id"]

        book_record_counts[book_id] = (
            book_record_counts.get(book_id, 0) + 1
        )

        record = build_record(
            current_book,
            current_content_type,
            current_content,
            book_record_counts[book_id],
        )

        if record:
            records.append(record)

        current_content = []

    for paragraph in paragraphs:
        book_match = detect_book_heading(
            paragraph
        )

        if book_match:
            flush_current_record()

            current_book = book_match
            current_content_type = None
            current_content = []

            continue

        section_match = detect_section_heading(
            paragraph
        )

        if section_match:
            flush_current_record()

            current_content_type = section_match
            current_content = []

            continue

        if (
            current_book is not None
            and current_content_type is not None
        ):
            current_content.append(paragraph)

    flush_current_record()

    return records


def summarize_records(
    records: list[dict],
) -> None:
    """
    Print record counts by book and content type.
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

        counts[key] = counts.get(key, 0) + 1

    for key, count in sorted(counts.items()):
        book_id, content_type = key

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

    print()
    print("=" * 70)
    print("PREVIEW")
    print("=" * 70)

    for record in records[:10]:
        print()
        print(
            f"{record['record_id']} | "
            f"{record['book_title']} | "
            f"{record['content_type']}"
        )

        if record["stance"]:
            print(
                f"Stance: {record['stance']}"
            )

        print()

        preview = record["text"][:500]

        print(preview)

        if len(record["text"]) > 500:
            print("...")