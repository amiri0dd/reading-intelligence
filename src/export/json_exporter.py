import json
from pathlib import Path


def save_record_as_json(record: dict, output_path: str) -> Path:
    """
    Save a structured screenshot record as a JSON file.

    Parameters
    ----------
    record:
        Structured screenshot metadata and OCR text.

    output_path:
        Destination path for the JSON file.

    Returns
    -------
    Path
        Path to the saved JSON file.
    """

    output_file = Path(output_path)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            record,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("Saved JSON record: {output_file}")

    return output_file