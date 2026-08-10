from src.export.concept_exporter import export_concept_pages
from src.export.obsidian_exporter import export_screenshot_folder_to_obsidian
from src.ingestion.batch_processor import process_folder
from src.linking.connection_exporter import export_connections_to_obsidian
from src.linking.semantic_linker import (
    find_semantic_connections,
    save_connections,
)


def run_pipeline() -> None:
    """
    Run the complete Reading Intelligence workflow.

    Pipeline:
    1. Process screenshots
    2. Export passages and books to Obsidian
    3. Build concept pages
    4. Find cross-book semantic connections
    5. Export accepted connections to Obsidian
    """

    print()
    print("=" * 70)
    print("READING INTELLIGENCE")
    print("=" * 70)

    # ---------------------------------------------------------
    # Step 1: Process screenshots
    # ---------------------------------------------------------

    print()
    print("STEP 1: PROCESSING SCREENSHOTS")
    print("=" * 70)

    process_folder(
        input_folder="screenshots",
        output_folder="processed",
    )

    # ---------------------------------------------------------
    # Step 2: Export passages and books to Obsidian
    # ---------------------------------------------------------

    print()
    print("STEP 2: UPDATING OBSIDIAN PASSAGES AND BOOKS")
    print("=" * 70)

    export_screenshot_folder_to_obsidian(
        input_folder="screenshots",
        vault_path="vault",
    )

    # ---------------------------------------------------------
    # Step 3: Build concept pages
    # ---------------------------------------------------------

    print()
    print("STEP 3: UPDATING CONCEPT PAGES")
    print("=" * 70)

    export_concept_pages(
        input_folder="screenshots",
        vault_path="vault",
    )

    # ---------------------------------------------------------
    # Step 4: Find cross-book semantic connections
    # ---------------------------------------------------------

    print()
    print("STEP 4: FINDING CROSS-BOOK CONNECTIONS")
    print("=" * 70)

    connections = find_semantic_connections(
        processed_folder="processed",
        minimum_similarity=0.55,
        max_connections_per_passage=3,
        cross_book_only=True,
    )

    save_connections(
        connections,
        output_path="processed/connections.json",
    )

    # ---------------------------------------------------------
    # Step 5: Write stronger connections into Obsidian
    # ---------------------------------------------------------

    print()
    print("STEP 5: UPDATING OBSIDIAN CONNECTIONS")
    print("=" * 70)

    export_connections_to_obsidian(
        connections_path="processed/connections.json",
        vault_path="vault",
        minimum_similarity=0.55,
    )

    # ---------------------------------------------------------
    # Complete
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("READING INTELLIGENCE UPDATE COMPLETE")
    print("=" * 70)
    print()
    print("Your Obsidian vault has been updated.")
    print()


if __name__ == "__main__":
    run_pipeline()