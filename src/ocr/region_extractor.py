from pathlib import Path

import pytesseract
from PIL import Image


def extract_regions(image_path: str, footer_height: int = 40) -> dict:
    """
    Extract the reading body and footer metadata from an Xteink screenshot.

    The footer is split into:
    - left: battery
    - center: chapter title
    - right: page/location + reading progress
    """

    image_file = Path(image_path)

    if not image_file.exists():
        raise FileNotFoundError(f"Could not find: {image_file}")

    with Image.open(image_file) as image:
        width, height = image.size

        footer_top = height - footer_height

        # Main reading area
        body = image.crop(
            (0, 0, width, footer_top)
        )

        # Footer regions
        footer_left = image.crop(
            (0, footer_top, int(width * 0.13), height)
        )

        footer_center = image.crop(
            (int(width * 0.10), footer_top, int(width * 0.84), height)
        )

        footer_right = image.crop(
            (int(width * 0.80), footer_top, width, height)
        )

        # OCR each region separately
        body_text = pytesseract.image_to_string(
            body
        ).strip()

        battery_text = pytesseract.image_to_string(
            footer_left,
            config="--psm 7"
        ).strip()

        chapter_text = pytesseract.image_to_string(
            footer_center,
            config="--psm 7"
        ).strip()

        reading_text = pytesseract.image_to_string(
            footer_right,
            config="--psm 7"
        ).strip()

    return {
        "body_text": body_text,
        "battery_text": battery_text,
        "chapter_text": chapter_text,
        "reading_text": reading_text,
    }


if __name__ == "__main__":
    results = extract_regions(
        "sample_data/sample_page.png"
    )

    print("BODY")
    print("=" * 60)
    print(results["body_text"])

    print("\nBATTERY")
    print("=" * 60)
    print(results["battery_text"])

    print("\nCHAPTER")
    print("=" * 60)
    print(results["chapter_text"])

    print("\nREADING METADATA")
    print("=" * 60)
    print(results["reading_text"])