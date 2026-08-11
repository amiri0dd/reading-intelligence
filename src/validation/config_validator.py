import csv
from pathlib import Path

from src.settings import (
    BOOKS_CSV,
    CHAPTER_ALIASES_CSV,
    CONCEPTS_CSV,
)


def read_csv(
    path: Path,
) -> list[dict]:
    """
    Read a CSV and return rows.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Missing configuration file: "
            f"{path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(
                f"{path.name} has no header."
            )

        return list(reader)


def require_columns(
    path: Path,
    required: set[str],
) -> list[dict]:
    """
    Validate required columns.
    """

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(
                f"{path.name} has no header."
            )

        missing = (
            required
            - set(reader.fieldnames)
        )

        if missing:
            raise ValueError(
                f"{path.name} is missing: "
                + ", ".join(
                    sorted(missing)
                )
            )

        return list(reader)


def validate_books() -> None:
    rows = require_columns(
        BOOKS_CSV,
        {
            "book_id",
            "title",
            "author",
        },
    )

    seen_ids = set()
    seen_titles = set()

    for row_number, row in enumerate(
        rows,
        start=2,
    ):
        book_id = (
            row.get("book_id", "")
            .strip()
        )

        title = (
            row.get("title", "")
            .strip()
        )

        if not book_id:
            raise ValueError(
                f"books.csv row "
                f"{row_number}: blank book_id"
            )

        if not title:
            raise ValueError(
                f"books.csv row "
                f"{row_number}: blank title"
            )

        if book_id in seen_ids:
            raise ValueError(
                f"Duplicate book_id: "
                f"{book_id}"
            )

        normalized_title = (
            title.casefold()
        )

        if normalized_title in seen_titles:
            raise ValueError(
                f"Duplicate book title: "
                f"{title}"
            )

        seen_ids.add(book_id)
        seen_titles.add(
            normalized_title
        )


def validate_chapter_aliases() -> None:
    rows = require_columns(
        CHAPTER_ALIASES_CSV,
        {
            "chapter_title",
            "book_id",
        },
    )

    valid_book_ids = {
        row["book_id"].strip()
        for row in read_csv(
            BOOKS_CSV
        )
        if row.get("book_id")
    }

    for row_number, row in enumerate(
        rows,
        start=2,
    ):
        chapter_title = (
            row.get("chapter_title", "")
            .strip()
        )

        book_id = (
            row.get("book_id", "")
            .strip()
        )

        if not chapter_title:
            raise ValueError(
                f"chapter_aliases.csv row "
                f"{row_number}: blank chapter_title"
            )

        if not book_id:
            raise ValueError(
                f"chapter_aliases.csv row "
                f"{row_number}: blank book_id"
            )

        if book_id not in valid_book_ids:
            raise ValueError(
                f"chapter_aliases.csv row "
                f"{row_number}: unknown "
                f"book_id {book_id}"
            )


def validate_concepts() -> None:
    rows = require_columns(
        CONCEPTS_CSV,
        {
            "concept_id",
            "concept_name",
            "parent_concept",
            "keywords",
        },
    )

    seen_ids = set()
    seen_names = set()

    for row_number, row in enumerate(
        rows,
        start=2,
    ):
        concept_id = (
            row.get("concept_id", "")
            .strip()
        )

        concept_name = (
            row.get("concept_name", "")
            .strip()
        )

        if not concept_id:
            raise ValueError(
                f"concepts.csv row "
                f"{row_number}: "
                f"blank concept_id"
            )

        if not concept_name:
            raise ValueError(
                f"concepts.csv row "
                f"{row_number}: "
                f"blank concept_name"
            )

        if concept_id in seen_ids:
            raise ValueError(
                f"Duplicate concept_id: "
                f"{concept_id}"
            )

        normalized_name = (
            concept_name.casefold()
        )

        if normalized_name in seen_names:
            raise ValueError(
                f"Duplicate concept name: "
                f"{concept_name}"
            )

        seen_ids.add(concept_id)
        seen_names.add(
            normalized_name
        )


def validate_all_configs() -> None:
    """
    Validate all configuration files.
    """

    validate_books()
    validate_chapter_aliases()
    validate_concepts()

    print(
        "Configuration validation passed."
    )


if __name__ == "__main__":
    validate_all_configs()