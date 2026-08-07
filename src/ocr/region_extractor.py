from pathlib import Path

import pytesseract
from PIL import Image


def extract_regions(image_path: str, footer_height: int = 40) -> dict:
    """
    Extract the main reading passage and footer metadata separately.

    Parameters
    ----------
    image_path:
        Path to the screenshot.

    footer_height:
        Height in pixels reserved for the footer area.

    Returns
    -------
    dict
        Dictionary containing OCR text from the body and footer.
    """

    image_file = Path(image_path)

    if not image_file.exists():
        raise FileNotFoundError(f"Could not find: {image_file}")

    with Image.open(image_file) as image:
        width, height = image.size

        body = image.crop((0, 0, width, height - footer_height))
        footer = image.crop((0, height - footer_height, width, height))

        body_text = pytesseract.image_to_string(body).strip()
        footer_text = pytesseract.image_to_string(
            footer,
            config="--psm 6"
        ).strip()

    return {
        "body_text": body_text,
        "footer_text": footer_text,
    }


if __name__ == "__main__":
    results = extract_regions("sample_data/sample_page.png")

    print("BODY")
    print("=" * 60)
    print(results["body_text"])

    print("\nFOOTER")
    print("=" * 60)
    print(results["footer_text"])