import re
from pathlib import Path

import pandas as pd

from src.classification.book_catalogue import get_book_by_id
from difflib import SequenceMatcher


def normalize_text(text: str | None) -> str:
    """
    Normalize chapter text for robust matching.
    """

    if not text:
        return ""

    text = text.casefold().strip()

    # Remove obvious OCR junk at the beginning.
    text = re.sub(
        r"^(ot|os)\s+",
        "",
        text,
    )

    # Remove stray punctuation/symbols at the beginning.
    text = re.sub(
        r"^[^\w]+",
        "",
        text,
    )

    # Remove one or more leading chapter numbers.
    text = re.sub(
        r"^(?:\d+\s*[\.\:\-\)]?\s*)+",
        "",
        text,
    )

    # Remove stray punctuation/symbols at the end.
    text = re.sub(
        r"[^\w]+$",
        "",
        text,
    )

    # Replace remaining punctuation with spaces.
    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
    )

    # Collapse repeated whitespace.
    text = " ".join(text.split())

    return text


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

    Matching order:
    1. Exact normalized chapter match
    2. Fuzzy chapter match
    3. Return unmatched
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

    # ---------------------------------------------------------
    # Step 1: Exact normalized match
    # ---------------------------------------------------------
    match = aliases[
        aliases["normalized_chapter"]
        == normalized_chapter
    ]

    if not match.empty:
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

    # ---------------------------------------------------------
    # Step 2: Fuzzy match
    # ---------------------------------------------------------
    best_match = None
    best_score = 0.0

    for _, row in aliases.iterrows():
        score = SequenceMatcher(
            None,
            normalized_chapter,
            row["normalized_chapter"],
        ).ratio()

        if score > best_score:
            best_score = score
            best_match = row

    if best_match is not None and best_score >= 0.85:
        book_id = best_match["book_id"]

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
            "match_method": "fuzzy_chapter",
            "confidence": round(best_score, 3),
        }

    # ---------------------------------------------------------
    # Step 3: No reliable match
    # ---------------------------------------------------------
    return {
        "matched": False,
        "book_id": None,
        "title": None,
        "author": None,
        "match_method": None,
        "confidence": round(best_score, 3),
    }


if __name__ == "__main__":
    sample_chapter = "9: Julius Evola"

    result = match_book_by_chapter(sample_chapter)

    print("BOOK MATCH")
    print("=" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")