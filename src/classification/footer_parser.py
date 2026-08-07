import re


def parse_footer(footer_text: str) -> dict:
    """
    Parse Xteink footer OCR into structured metadata.

    Handles footer text such as:

    65% 1. The Paleontology of Iranian Nationalism 31/118 6%

    where:
    - 65% = battery level
    - chapter title = The Paleontology...
    - 31/118 = reading location
    - 6% = reading progress
    """

    cleaned = " ".join(footer_text.split())

    # Find page/location information.
    page_match = re.search(r"(\d+)\s*/\s*(\d+)", cleaned)

    current_page = None
    total_pages = None
    progress_percent = None
    chapter = None

    if page_match:
        current_page = int(page_match.group(1))
        total_pages = int(page_match.group(2))

        # Everything before 31/118 should contain the chapter,
        # potentially preceded by battery percentage.
        chapter_part = cleaned[:page_match.start()].strip()

        # Remove a leading battery percentage such as "65%".
        chapter_part = re.sub(
            r"^\d+\s*%\s*",
            "",
            chapter_part
        ).strip()

        chapter = chapter_part or None

        # Reading progress should occur AFTER the page/location value.
        after_page = cleaned[page_match.end():]

        progress_match = re.search(
            r"(\d+)\s*%",
            after_page
        )

        if progress_match:
            progress_percent = int(progress_match.group(1))

    else:
        # Fallback in case a screenshot lacks page/location information.
        percentages = re.findall(r"(\d+)\s*%", cleaned)

        if percentages:
            progress_percent = int(percentages[-1])

    return {
        "chapter": chapter,
        "current_page": current_page,
        "total_pages": total_pages,
        "progress_percent": progress_percent,
    }


if __name__ == "__main__":
    sample = (
        "65% 1. The Paleontology of Iranian Nationalism "
        "31/118 6%"
    )

    result = parse_footer(sample)

    print(result)