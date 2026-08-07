from pathlib import Path

import pandas as pd

from src.classification.book_catalogue import get_book_by_id


def normalize_text(text: str | None) -> str:
    """
    Normalize text for reliable comparisons.
    """

    if not text:
        return ""

    return " ".join(
        text.casefold().strip().split()
    )


def load_chapter_aliases(
    aliases_path: str = "config/chapter_aliases.csv",
) -> pd.DataFrame:
    """
    Load known chapter-to-book mappings.
    """

    aliases_file = Path(aliases_path)

    if not aliases_file.exists():
        raise FileNotFoundError(
            f"Could not find chapter aliases: {aliases_file}"
        )

    aliases = pd.read_csv(aliases_file)

    required_columns = {
        "chapter_title",
        "book_id",
    }

    missing_columns = required_columns - set(aliases.columns)

    if missing_columns:
        raise ValueError(
            "Chapter aliases file is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    aliases["chapter_title"] = (
        aliases["chapter_title"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    aliases["book_id"] = (
        aliases["book_id"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    aliases["normalized_chapter"] = (
        aliases["chapter_title"]
        .apply(normalize_text)
    )

    return aliases


def match_book_by_chapter(
    chapter_title: str | None,
    aliases_path: str = "config/chapter_aliases.csv",
    catalogue_path: str = "config/books.csv",
) -> dict:
    """
    Match an extracted chapter title to a known book.

    Returns a structured match result.
    """

    normalized_chapter = normalize_text(chapter_title)

    if not normalized_chapter:
        return {
            "matched": False,
            "book_id": None,
            "title": None,
            "author": None,
            "match_method": None,
            "confidence": 0.0,
        }

    aliases = load_chapter_aliases(aliases_path)

    match = aliases[
        aliases["normalized_chapter"]
        == normalized_chapter
    ]

    if match.empty:
        return {
            "matched": False,
            "book_id": None,
            "title": None,
            "author": None,
            "match_method": None,
            "confidence": 0.0,
        }

    book_id = match.iloc[0]["book_id"]

    book = get_book_by_id(
        book_id,
        catalogue_path=catalogue_path,
    )

    if book is None:
        raise ValueError(
            f"Chapter alias points to unknown book_id: {book_id}"
        )

    return {
        "matched": True,
        "book_id": book["book_id"],
        "title": book["title"],
        "author": book["author"],
        "match_method": "known_chapter",
        "confidence": 1.0,
    }


if __name__ == "__main__":
    sample_chapter = (
        "1. The Paleontology of Iranian Nationalism"
    )

    print("TEST CHAPTER")
    print(repr(sample_chapter))
    print("Normalized:", repr(normalize_text(sample_chapter)))

    print("\nALIASES")
    print("=" * 60)

    aliases = load_chapter_aliases()

    for _, row in aliases.iterrows():
        print("Original:", repr(row["chapter_title"]))
        print("Normalized:", repr(row["normalized_chapter"]))
        print("Book ID:", repr(row["book_id"]))
        print()

    result = match_book_by_chapter(sample_chapter)

    print("\nBOOK MATCH")
    print("=" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")