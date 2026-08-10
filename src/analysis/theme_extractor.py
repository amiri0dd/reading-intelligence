import re

from src.classification.concept_catalogue import (
    load_concept_catalogue,
)


def normalize_text(text: str) -> str:
    """
    Normalize passage text for keyword matching.
    """

    text = text.casefold()

    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
    )

    text = " ".join(text.split())

    return text


def extract_themes(
    text: str,
    catalogue_path: str = "config/concepts.csv",
) -> list[dict]:
    """
    Identify controlled concepts appearing in passage text.

    Returns a list of matched concepts with the
    keywords that triggered each match.
    """

    normalized_text = normalize_text(text)

    concepts = load_concept_catalogue(
        catalogue_path
    )

    matches = []

    for _, concept in concepts.iterrows():

        keywords = [
            keyword.strip()
            for keyword
            in concept["keywords"].split(",")
            if keyword.strip()
        ]

        matched_keywords = []

        for keyword in keywords:
            normalized_keyword = normalize_text(keyword)

            pattern = (
                r"\b"
                + re.escape(normalized_keyword)
                + r"\b"
            )

            if re.search(pattern, normalized_text):
                matched_keywords.append(keyword)

        if matched_keywords:
            matches.append(
                {
                    "concept_id": concept["concept_id"],
                    "concept_name": concept["concept_name"],
                    "parent_concept": concept["parent_concept"],
                    "matched_keywords": matched_keywords,
                }
            )

    return matches


if __name__ == "__main__":
    from src.ingestion.screenshot_processor import process_screenshot

    record = process_screenshot(
        "screenshots/sample_page.bmp"
    )

    themes = extract_themes(
        record["body_text"]
    )

    print("DETECTED THEMES")
    print("=" * 60)

    for theme in themes:
        print(
            f"{theme['concept_name']} "
            f"-> {theme['matched_keywords']}"
        )