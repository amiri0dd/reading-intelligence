from pathlib import Path

import pytesseract
from PIL import Image


def extract_text(image_path: str) -> str:
    """
    Extract text from an image using Tesseract OCR.

    Parameters
    ----------
    image_path:
        Path to the image file.

    Returns
    -------
    str
        Extracted OCR text.
    """

    image_file = Path(image_path)

    if not image_file.exists():
        raise FileNotFoundError(f"Could not find: {image_file}")

    with Image.open(image_file) as image:
        text = pytesseract.image_to_string(image)

    return text.strip()


if __name__ == "__main__":
    text = extract_text("sample_data/sample_page.png")

    print("OCR RESULT")
    print("=" * 50)
    print(text)