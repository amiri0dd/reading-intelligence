from pathlib import Path

from src.export.json_exporter import save_record_as_json
from src.ingestion.screenshot_processor import process_screenshot


def process_folder(input_folder: str, output_folder: str = "processed") -> list[dict]:
    """
    Process every BMP screenshot in a folder.

    Parameters
    ----------
    input_folder:
        Folder containing Xteink BMP screenshots.

    output_folder:
        Folder where JSON records should be saved.

    Returns
    -------
    list[dict]
        Structured records for all successfully processed screenshots.
    """

    input_path = Path(input_folder)
    output_path = Path(output_folder)

    if not input_path.exists():
        raise FileNotFoundError(f"Could not find folder: {input_path}")

    bmp_files = sorted(input_path.glob("*.bmp"))

    if not bmp_files:
        print(f"No BMP files found in: {input_path}")
        return []

    print(f"Found {len(bmp_files)} BMP screenshot(s).")
    print("=" * 60)

    records = []

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
            print(f"Match Method: {record['book_match_method']}")
            print(f"Match Confidence: {record['book_match_confidence']}")






        except Exception as error:
            print(f"Status: Failed")
            print(f"Error: {error}")

    print("\n" + "=" * 60)
    print("BATCH COMPLETE")
    print(f"Successful: {len(records)}")
    print(f"Failed: {len(bmp_files) - len(records)}")

    return records


if __name__ == "__main__":
    process_folder("sample_data")