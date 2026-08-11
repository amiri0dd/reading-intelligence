from collections.abc import Callable

from src.settings import (
    SCREENSHOTS_DIR,
    DEFAULT_TYPED_NOTES_FILE,
    BOOKS_CSV,
)

from src.validation.config_validator import (
    validate_all_configs,
)

from src.ingestion.batch_processor import (
    process_folder,
)

from src.export.obsidian_exporter import (
    export_screenshot_folder_to_obsidian,
)

from src.export.typed_notes_exporter import (
    export_typed_notes_to_obsidian,
)

from src.export.concept_exporter import (
    export_concept_pages,
)

from src.linking.semantic_linker import (
    find_semantic_connections,
    save_connections,
)

from src.linking.connection_exporter import (
    export_connections_to_obsidian,
)


def count_books() -> int:
    """
    Count configured books without introducing
    another pandas dependency here.
    """

    if not BOOKS_CSV.exists():
        return 0

    with BOOKS_CSV.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        # Subtract header.
        return max(
            sum(
                1
                for line in file
                if line.strip()
            )
            - 1,
            0,
        )


def print_pipeline_summary() -> None:
    """
    Show what the pipeline is about to process.
    """

    screenshot_count = (
        len(
            list(
                SCREENSHOTS_DIR.glob(
                    "*.bmp"
                )
            )
        )
        if SCREENSHOTS_DIR.exists()
        else 0
    )

    typed_notes_present = (
        DEFAULT_TYPED_NOTES_FILE.exists()
    )

    print()
    print("=" * 70)
    print("READING INTELLIGENCE v1.0")
    print("=" * 70)

    print(
        f"Configured books: "
        f"{count_books()}"
    )

    print(
        f"Xteink screenshots: "
        f"{screenshot_count}"
    )

    print(
        "Typed notes document: "
        + (
            "found"
            if typed_notes_present
            else "not found"
        )
    )

    print()


def run_stage(
    number: int,
    title: str,
    function: Callable,
):
    """
    Run one pipeline stage and make failures easy
    to identify.
    """

    print()
    print("=" * 70)
    print(
        f"STEP {number}: {title}"
    )
    print("=" * 70)

    try:
        result = function()

    except Exception as error:
        print()
        print(
            f"STEP {number} FAILED: "
            f"{title}"
        )

        print(
            f"{type(error).__name__}: "
            f"{error}"
        )

        raise

    print(
        f"STEP {number} COMPLETE"
    )

    return result


def process_screenshots():
    if not SCREENSHOTS_DIR.exists():
        print(
            "No screenshots directory. "
            "Skipping."
        )
        return

    if not list(
        SCREENSHOTS_DIR.glob("*.bmp")
    ):
        print(
            "No BMP screenshots found. "
            "Skipping."
        )
        return

        process_folder(str(SCREENSHOTS_DIR))


def export_screenshots():
    if not SCREENSHOTS_DIR.exists():
        print(
            "No screenshots directory. "
            "Skipping."
        )
        return

    if not list(
        SCREENSHOTS_DIR.glob("*.bmp")
    ):
        print(
            "No BMP screenshots found. "
            "Skipping."
        )
        return

    export_screenshot_folder_to_obsidian()


def process_typed_notes():
    if not DEFAULT_TYPED_NOTES_FILE.exists():
        print(
            "No typed notes DOCX found. "
            "Skipping."
        )
        return

    export_typed_notes_to_obsidian(
        str(DEFAULT_TYPED_NOTES_FILE)
    )


def build_connections():
    connections = (
        find_semantic_connections(
            minimum_similarity=0.55,
            max_connections_per_passage=3,
            cross_book_only=True,
        )
    )

    save_connections(
        connections
    )

    return connections


def run_pipeline() -> None:
    """
    Run the complete Reading Intelligence pipeline.
    """

    print_pipeline_summary()

    run_stage(
        1,
        "VALIDATE CONFIGURATION",
        validate_all_configs,
    )

    run_stage(
        2,
        "PROCESS XTEINK SCREENSHOTS",
        process_screenshots,
    )

    run_stage(
        3,
        "EXPORT XTEINK NOTES TO OBSIDIAN",
        export_screenshots,
    )

    run_stage(
        4,
        "PROCESS TYPED READING NOTES",
        process_typed_notes,
    )

    run_stage(
        5,
        "UPDATE CONCEPT PAGES",
        export_concept_pages,
    )

    run_stage(
        6,
        "BUILD CROSS-BOOK CONNECTIONS",
        build_connections,
    )

    run_stage(
        7,
        "WRITE CONNECTIONS TO OBSIDIAN",
        export_connections_to_obsidian,
    )

    print()
    print("=" * 70)
    print(
        "READING INTELLIGENCE v1.0 "
        "UPDATE COMPLETE"
    )
    print("=" * 70)

    print()
    print(
        "Open your Obsidian vault "
        "to explore the updated library."
    )


if __name__ == "__main__":
    run_pipeline()