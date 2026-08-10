from pathlib import Path

from src.ingestion.batch_processor import process_folder
from src.export.obsidian_exporter import (
    export_screenshot_folder_to_obsidian,
)
from src.export.concept_exporter import (
    export_concept_pages,
)
from src.export.typed_notes_exporter import (
    export_typed_notes_to_obsidian,
)
from src.linking.semantic_linker import (
    find_semantic_connections,
    save_connections,
)
from src.linking.connection_exporter import (
    export_connections_to_obsidian,
)


SCREENSHOTS_DIR = Path("screenshots")
TYPED_NOTES_FILE = Path(
    "typed_notes/quote_analysis.docx"
)


def print_stage(number: int, title: str) -> None:
    print()
    print("=" * 70)
    print(
        f"STEP {number}: {title}"
    )
    print("=" * 70)


def run_pipeline() -> None:

    print()
    print("=" * 70)
    print("READING INTELLIGENCE")
    print("FULL UPDATE PIPELINE")
    print("=" * 70)

    # --------------------------------------------------
    # 1. Xteink screenshots
    # --------------------------------------------------

    print_stage(
        1,
        "PROCESS XTEINK SCREENSHOTS",
    )

    if SCREENSHOTS_DIR.exists():

        process_folder()

    else:
        print(
            "No screenshots folder found. "
            "Skipping screenshot processing."
        )

    # --------------------------------------------------
    # 2. Screenshot → Obsidian
    # --------------------------------------------------

    print_stage(
        2,
        "EXPORT XTEINK PASSAGES TO OBSIDIAN",
    )

    if SCREENSHOTS_DIR.exists():

        export_screenshot_folder_to_obsidian()

    else:
        print(
            "Skipping Xteink Obsidian export."
        )

    # --------------------------------------------------
    # 3. Typed notes
    # --------------------------------------------------

    print_stage(
        3,
        "PROCESS TYPED READING NOTES",
    )

    if TYPED_NOTES_FILE.exists():

        export_typed_notes_to_obsidian(
            str(TYPED_NOTES_FILE)
        )

    else:
        print(
            "No typed notes DOCX found. "
            "Skipping typed-note processing."
        )

    # --------------------------------------------------
    # 4. Concepts
    # --------------------------------------------------

    print_stage(
        4,
        "UPDATE CONCEPT PAGES",
    )

    export_concept_pages()

    # --------------------------------------------------
    # 5. Semantic relationships
    # --------------------------------------------------

    print_stage(
        5,
        "BUILD CROSS-BOOK CONNECTIONS",
    )

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

    # --------------------------------------------------
    # 6. Write connections to Obsidian
    # --------------------------------------------------

    print_stage(
        6,
        "WRITE CONNECTIONS TO OBSIDIAN",
    )

    export_connections_to_obsidian(
        minimum_similarity=0.55
    )

    print()
    print("=" * 70)
    print("READING INTELLIGENCE UPDATE COMPLETE")
    print("=" * 70)

    print()
    print(
        "Your Obsidian vault is ready."
    )


if __name__ == "__main__":
    run_pipeline()