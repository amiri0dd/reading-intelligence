from pathlib import Path

from src.ingestion.image_converter import convert_bmp_to_png
from src.ocr.region_extractor import extract_regions
from src.classification.footer_parser import parse_footer


def process_screenshot(image_path: str) -> dict:
    """
    Process one Xteink screenshot from BMP to structured metadata.

    Parameters
    ----------
    image_path:
        Path to the original BMP screenshot.

    Returns
    -------
    dict
        Structured screenshot record containing:
        - original image path
        - converted PNG path
        - body OCR text
        - footer OCR text
        - chapter
        - current page
        - total pages
        - progress percentage
    """

    input_file = Path(image_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Could not find: {input_file}")

    # Step 1: Convert BMP to PNG
    png_path = convert_bmp_to_png(str(input_file))

    # Step 2: OCR body and footer separately
    regions = extract_regions(str(png_path))

    # Step 3: Parse footer metadata
    metadata = parse_footer(regions["footer_text"])

    # Step 4: Combine everything into one record
    record = {
        "original_image": str(input_file),
        "png_image": str(png_path),
        "body_text": regions["body_text"],
        "footer_text": regions["footer_text"],
        "chapter": metadata["chapter"],
        "current_page": metadata["current_page"],
        "total_pages": metadata["total_pages"],
        "progress_percent": metadata["progress_percent"],
    }

    return record


if __name__ == "__main__":
    result = process_screenshot("sample_data/sample_page.bmp")

    print("\nSTRUCTURED RECORD")
    print("=" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")