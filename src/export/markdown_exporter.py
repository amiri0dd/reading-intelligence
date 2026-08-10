from pathlib import Path
import shutil


def sanitize_filename(text: str) -> str:
    """
    Create a Windows-safe filename.
    """

    invalid_chars = '<>:"/\\|?*'

    for char in invalid_chars:
        text = text.replace(char, "-")

    return " ".join(text.split()).strip()


def export_passage_to_obsidian(
    record: dict,
    vault_path: str = "vault",
) -> Path:
    """
    Export one processed screenshot record as an
    Obsidian-compatible Markdown note.

    Also copies the PNG screenshot into:
    vault/Attachments/Images/
    """

    vault = Path(vault_path)

    passages_folder = vault / "Passages"
    images_folder = vault / "Attachments" / "Images"

    passages_folder.mkdir(parents=True, exist_ok=True)
    images_folder.mkdir(parents=True, exist_ok=True)

    source_image = Path(record["png_image"])

    if not source_image.exists():
        raise FileNotFoundError(
            f"Could not find PNG image: {source_image}"
        )

    # Copy screenshot into the Obsidian vault.
    destination_image = images_folder / source_image.name

    shutil.copy2(
        source_image,
        destination_image
    )

    book_title = record["book_title"] or "Unassigned"
    author = record["author"] or "Unknown"
    chapter = record["chapter"] or "Unknown Chapter"

    current_page = record["current_page"]
    total_pages = record["total_pages"]
    progress = record["progress_percent"]

    location = ""

    if current_page is not None and total_pages is not None:
        location = f"{current_page}/{total_pages}"

    progress_display = (
        f"{progress}%"
        if progress is not None
        else ""
    )

    # Use a Windows-safe filename for the book note link.
    book_note_name = sanitize_filename(
        book_title
    )

    # Build theme links.
    theme_links = []

    for theme in record.get("themes", []):
        theme_links.append(
            f"- [[{theme['concept_name']}]]"
        )

    themes_markdown = (
        "\n".join(theme_links)
        if theme_links
        else "_No concepts detected yet._"
    )

    # Create a unique passage note filename.
    note_title = sanitize_filename(
        f"{book_title} - {chapter} - {source_image.stem}"
    )

    note_path = passages_folder / f"{note_title}.md"

    markdown = f"""---
type: passage
book_id: "{record['book_id'] or ''}"
book: "{book_title}"
author: "{author}"
chapter: "{chapter}"
location: "{location}"
progress_percent: {progress if progress is not None else 'null'}
match_method: "{record['book_match_method'] or ''}"
match_confidence: {record['book_match_confidence']}
---

# {chapter}

## Source

**Book:** [[{book_note_name}|{book_title}]]

**Author:** {author}

**Chapter:** {chapter}

**Location:** {location}

**Progress:** {progress_display}

![[Attachments/Images/{destination_image.name}]]

## Extracted Passage

{record["body_text"]}

## My Note

> Why did this passage stand out to me?

## AI Analysis

_To be generated later._

## Themes

{themes_markdown}

## Connections

_To be added._
"""

    note_path.write_text(
        markdown,
        encoding="utf-8"
    )

    print(f"Created Obsidian note: {note_path}")

    return note_path