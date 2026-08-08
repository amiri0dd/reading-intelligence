from pathlib import Path

from src.export.json_exporter import save_record_as_json
from src.ingestion.screenshot_processor import process_screenshot


def process_folder(
    input_folder: str,
    output_folder: str = "processed"
) -> list[dict]:
    """
    Process every BMP screenshot in a folder.
    """

    input_path = Path(input_folder)
    output_path = Path(output_folder)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Could not find folder: {input_path}"
        )

    bmp_files = sorted(input_path.glob("*.bmp"))

    if not bmp_files:
        print(f"No BMP files found in: {input_path}")
        return []

    print(f"Found {len(bmp_files)} BMP screenshot(s).")
    print("=" * 60)

    records = []
    failed_files = []

    for index, bmp_file in enumerate(bmp_files, start=1):
        print(f"\nProcessing {index}/{len(bmp_files)}")
        print(f"File: {bmp_file.name}")

        try:
            record = process_screenshot(str(bmp_file))

            json_path = output_path / f"{bmp_file.stem}.json"

            save_record_as_json(
                record,
                str(json_path)
            )

            records.append(record)

            print("Status: Success")
            print(f"Book ID: {record['book_id']}")
            print(f"Book Title: {record['book_title']}")
            print(f"Chapter: {record['chapter']}")
            print(
                f"Match Method: "
                f"{record['book_match_method']}"
            )
            print(
                f"Match Confidence: "
                f"{record['book_match_confidence']}"
            )

        except Exception as error:
            print("Status: Failed")
            print(f"Error: {error}")

            failed_files.append(
                {
                    "file": bmp_file.name,
                    "error": str(error),
                }
            )

    matched_records = [
        record
        for record in records
        if record["book_id"] is not None
    ]

    unmatched_records = [
        record
        for record in records
        if record["book_id"] is None
    ]

    print("\n" + "=" * 60)
    print("BATCH COMPLETE")
    print(f"Processed successfully: {len(records)}")
    print(f"Processing failures: {len(failed_files)}")
    print(f"Matched to a book: {len(matched_records)}")
    print(f"Unmatched: {len(unmatched_records)}")

    if failed_files:
        print("\nFAILED FILES")
        print("=" * 60)

        for item in failed_files:
            print(f"File: {item['file']}")
            print(f"Error: {item['error']}")
            print("-" * 60)

    if unmatched_records:
        print("\nUNMATCHED CHAPTERS")
        print("=" * 60)

        for record in unmatched_records:
            filename = Path(
                record["original_image"]
            ).name

            print(
                f"{filename}: "
                f"{record['chapter']}"
            )

    return records


if __name__ == "__main__":
    process_folder("screenshots")