import re


def parse_footer(
    chapter_text: str,
    reading_text: str,
) -> dict:
    """
    Parse isolated Xteink footer regions.

    Parameters
    ----------
    chapter_text:
        OCR text from the center footer region.

    reading_text:
        OCR text from the right footer region.

    Returns
    -------
    dict
        Chapter title, current page, total pages,
        and reading progress percentage.
    """

    chapter = " ".join(chapter_text.split()).strip()

    reading = " ".join(reading_text.split()).strip()

    page_match = re.search(
        r"(\d+)\s*/\s*(\d+)",
        reading
    )

    progress_match = re.search(
        r"(\d+)\s*%",
        reading
    )

    current_page = None
    total_pages = None
    progress_percent = None

    if page_match:
        current_page = int(page_match.group(1))
        total_pages = int(page_match.group(2))

    if progress_match:
        progress_percent = int(progress_match.group(1))

    return {
        "chapter": chapter or None,
        "current_page": current_page,
        "total_pages": total_pages,
        "progress_percent": progress_percent,
    }