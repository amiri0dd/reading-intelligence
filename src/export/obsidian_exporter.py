from collections import defaultdict
from pathlib import Path

from src.export.markdown_exporter import export_passage_to_obsidian
from src.ingestion.screenshot_processor import process_screenshot


def sanitize_filename(text: str) -> str:
    """
    Create a Windows-safe filename.
    """

    invalid_chars = '<>:"/\\|?*'

    for char in invalid_chars:
        text = text.replace(char, "-")

    return " ".join(text.split()).strip()


def export_book_page(
    book_title: str,
    author: str,
    book_id: str,
    passage_notes: list[dict],
    vault_path: str = "vault",
) -> Path:
    """
    Create or replace one Obsidian book page containing
    links to all exported passage notes for that book.
    """

    vault = Path(vault_path)
    books_folder = vault / "Books"

    books_folder.mkdir(parents=True, exist_ok=True)

    filename = sanitize_filename(book_title)
    book_path = books_folder / f"{filename}.md"

    lines = [
        "---",
        "type: book",
        f'book_id: "{book_id}"',
        f'author: "{author}"',
        "---",
        "",
        f"# {book_title}",
        "",
        f"**Author:** {author}",
        "",
        "## Saved Passages",
        "",
    ]

    sorted_passages = sorted(
        passage_notes,
        key=lambda item: (
            item["current_page"]
            if item["current_page"] is not None
            else 999999
        )
    )

    for passage in sorted_passages:
        note_name = passage["note_path"].stem

        chapter = passage["chapter"] or "Unknown Chapter"

        if (
            passage["current_page"] is not None
            and passage["total_pages"] is not None
        ):
            location = (
                f"{passage['current_page']}/"
                f"{passage['total_pages']}"
            )
        else:
            location = ""

        display = chapter

        if location:
            display += f" ({location})"

        lines.append(
            f"- [[{note_name}|{display}]]"
        )

    lines.extend(
        [
            "",
            "## Book-Level Notes",
            "",
            "_Add your overall notes about this book here._",
            "",
            "## Recurring Themes",
            "",
            "_To be generated later._",
            "",
            "## Synthesis",
            "",
            "_To be generated later._",
            "",
        ]
    )

    book_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(f"Created book page: {book_path}")

    return book_path


def export_screenshot_folder_to_obsidian(
    input_folder: str = "screenshots",
    vault_path: str = "vault",
) -> None:
    """
    Process every BMP screenshot and export the results
    into an Obsidian vault.

    Creates:
    - one passage note per screenshot
    - one image attachment per screenshot
    - one book page per matched book
    """

    input_path = Path(input_folder)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Could not find screenshot folder: {input_path}"
        )

    bmp_files = sorted(input_path.glob("*.bmp"))

    if not bmp_files:
        print(f"No BMP screenshots found in: {input_path}")
        return

    print(
        f"Found {len(bmp_files)} screenshot(s) for Obsidian export."
    )
    print("=" * 60)

    books = defaultdict(list)

    successful = 0
    failed = []

    for index, bmp_file in enumerate(bmp_files, start=1):
        print(
            f"\nExporting {index}/{len(bmp_files)}: "
            f"{bmp_file.name}"
        )

        try:
            record = process_screenshot(
                str(bmp_file)
            )

            if record["book_id"] is None:
                print(
                    "Skipped: screenshot is not matched "
                    "to a known book."
                )
                continue

            note_path = export_passage_to_obsidian(
                record,
                vault_path=vault_path,
            )

            record["note_path"] = note_path

            books[record["book_id"]].append(
                record
            )

            successful += 1

        except Exception as error:
            failed.append(
                {
                    "file": bmp_file.name,
                    "error": str(error),
                }
            )

            print(f"Failed: {error}")

    print("\n" + "=" * 60)
    print("CREATING BOOK PAGES")

    for book_id, passages in books.items():
        first = passages[0]

        export_book_page(
            book_title=first["book_title"],
            author=first["author"],
            book_id=book_id,
            passage_notes=passages,
            vault_path=vault_path,
        )

    print("\n" + "=" * 60)
    print("OBSIDIAN EXPORT COMPLETE")
    print(f"Passage notes created: {successful}")
    print(f"Books created: {len(books)}")
    print(f"Failures: {len(failed)}")

    if failed:
        print("\nFAILED EXPORTS")
        print("=" * 60)

        for item in failed:
            print(f"File: {item['file']}")
            print(f"Error: {item['error']}")
            print("-" * 60)


if __name__ == "__main__":
    export_screenshot_folder_to_obsidian()