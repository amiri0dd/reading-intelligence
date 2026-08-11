from src.settings import (
    BOOKS_CSV,
    CONCEPTS_CSV,
    SCREENSHOTS_DIR,
    DEFAULT_TYPED_NOTES_FILE,
)

from src.validation.config_validator import (
    validate_all_configs,
)

from src.ingestion.typed_notes_importer import (
    parse_typed_document,
)

from src.linking.semantic_linker import (
    load_semantic_records,
)


def run_smoke_test() -> None:

    print()
    print("=" * 70)
    print("READING INTELLIGENCE SMOKE TEST")
    print("=" * 70)

    print()
    print("1. Checking configuration files...")

    assert BOOKS_CSV.exists(), (
        "books.csv is missing."
    )

    assert CONCEPTS_CSV.exists(), (
        "concepts.csv is missing."
    )

    validate_all_configs()

    print("PASS")

    print()
    print("2. Checking typed notes...")

    if DEFAULT_TYPED_NOTES_FILE.exists():

        records = parse_typed_document(
            DEFAULT_TYPED_NOTES_FILE
        )

        assert records, (
            "Typed notes file produced "
            "zero records."
        )

        print(
            f"PASS: {len(records)} "
            f"typed records parsed."
        )

    else:
        print(
            "SKIP: no typed notes DOCX."
        )

    print()
    print("3. Checking screenshots...")

    screenshots = (
        list(
            SCREENSHOTS_DIR.glob(
                "*.bmp"
            )
        )
        if SCREENSHOTS_DIR.exists()
        else []
    )

    print(
        f"PASS: {len(screenshots)} "
        f"BMP screenshots found."
    )

    print()
    print("4. Checking semantic records...")

    semantic_records = (
        load_semantic_records()
    )

    assert semantic_records, (
        "No semantic records found."
    )

    print(
        f"PASS: {len(semantic_records)} "
        f"semantic records loaded."
    )

    print()
    print("=" * 70)
    print("SMOKE TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_smoke_test()