from pathlib import Path

from src.classification.book_matcher import match_book_by_chapter
from src.classification.footer_parser import parse_footer
from src.export.json_exporter import save_record_as_json
from src.ingestion.image_converter import convert_bmp_to_png
from src.ocr.region_extractor import extract_regions
from src.export.markdown_exporter import export_passage_to_obsidian


def process_screenshot(image_path: str) -> dict:
    """
    Process one Xteink screenshot from BMP to structured metadata.
    """

    input_file = Path(image_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Could not find: {input_file}")

    # Step 1: Convert BMP to PNG
    png_path = convert_bmp_to_png(str(input_file))

    # Step 2: OCR body and footer regions
    regions = extract_regions(str(png_path))

    # Step 3: Parse chapter and reading metadata
    metadata = parse_footer(
        regions["chapter_text"],
        regions["reading_text"],
    )

    # Step 4: Match chapter to a known book
    book_match = match_book_by_chapter(
        metadata["chapter"]
    )

    # Step 5: Combine everything into one record
    record = {
        "original_image": str(input_file),
        "png_image": str(png_path),

        "book_id": book_match["book_id"],
        "book_title": book_match["title"],
        "author": book_match["author"],
        "book_match_method": book_match["match_method"],
        "book_match_confidence": book_match["confidence"],

        "chapter": metadata["chapter"],
        "current_page": metadata["current_page"],
        "total_pages": metadata["total_pages"],
        "progress_percent": metadata["progress_percent"],

        "body_text": regions["body_text"],
        "battery_text": regions["battery_text"],
        "chapter_text": regions["chapter_text"],
        "reading_text": regions["reading_text"],
    }

    return record


if __name__ == "__main__":
    result = process_screenshot("screenshots/sample_page.bmp")

    print("\nSTRUCTURED RECORD")
    print("=" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")

    save_record_as_json(
        result,
        "processed/sample_page.json"
    )
    
    export_passage_to_obsidian(
    result,
    "vault"
)