from collections import defaultdict
from pathlib import Path

from src.classification.concept_catalogue import load_concept_catalogue
from src.export.markdown_exporter import sanitize_filename
from src.ingestion.screenshot_processor import process_screenshot


def export_concept_pages(
    input_folder: str = "screenshots",
    vault_path: str = "vault",
) -> None:
    """
    Build Obsidian Concept pages from all screenshot records.

    Each Concept page includes:
    - parent concept
    - books where the concept appears
    - passages where the concept appears
    - matched keywords
    - space for personal interpretation
    - space for future AI synthesis
    """

    input_path = Path(input_folder)
    vault = Path(vault_path)

    concepts_folder = vault / "Concepts"
    concepts_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"Could not find screenshot folder: {input_path}"
        )

    bmp_files = sorted(
        input_path.glob("*.bmp")
    )

    if not bmp_files:
        print(
            f"No BMP screenshots found in: {input_path}"
        )
        return

    # Load canonical concept metadata.
    concept_catalogue = load_concept_catalogue()

    concept_data = defaultdict(
        lambda: {
            "concept_id": None,
            "parent_concept": "",
            "books": set(),
            "passages": [],
            "keywords": set(),
        }
    )

    print(
        f"Scanning {len(bmp_files)} screenshot(s) "
        "for concepts..."
    )
    print("=" * 60)

    for index, bmp_file in enumerate(
        bmp_files,
        start=1,
    ):
        print(
            f"Processing {index}/{len(bmp_files)}: "
            f"{bmp_file.name}"
        )

        try:
            record = process_screenshot(
                str(bmp_file)
            )

        except Exception as error:
            print(
                f"Skipped due to error: {error}"
            )
            continue

        book_title = (
            record["book_title"]
            or "Unassigned"
        )

        chapter = (
            record["chapter"]
            or "Unknown Chapter"
        )

        source_image = Path(
            record["png_image"]
        )

        passage_note_name = (
            sanitize_filename(
                f"{book_title} - "
                f"{chapter} - "
                f"{source_image.stem}"
            )
        )

        book_note_name = sanitize_filename(
            book_title
        )

        for theme in record.get(
            "themes",
            [],
        ):
            concept_name = theme[
                "concept_name"
            ]

            data = concept_data[
                concept_name
            ]

            data["concept_id"] = theme[
                "concept_id"
            ]

            data["parent_concept"] = theme[
                "parent_concept"
            ]

            data["books"].add(
                (
                    book_note_name,
                    book_title,
                )
            )

            data["passages"].append(
                {
                    "note_name": passage_note_name,
                    "chapter": chapter,
                    "book_title": book_title,
                    "current_page": record[
                        "current_page"
                    ],
                    "total_pages": record[
                        "total_pages"
                    ],
                }
            )

            for keyword in theme.get(
                "matched_keywords",
                [],
            ):
                data["keywords"].add(
                    keyword
                )

    # Create one page per concept in the catalogue,
    # including concepts not yet observed.
    for _, concept in (
        concept_catalogue.iterrows()
    ):
        concept_name = concept[
            "concept_name"
        ]

        concept_id = concept[
            "concept_id"
        ]

        parent_concept = concept[
            "parent_concept"
        ]

        data = concept_data.get(
            concept_name,
            {
                "concept_id": concept_id,
                "parent_concept": parent_concept,
                "books": set(),
                "passages": [],
                "keywords": set(),
            },
        )

        # Prefer canonical catalogue values.
        data["concept_id"] = concept_id
        data["parent_concept"] = (
            parent_concept
        )

        concept_filename = (
            sanitize_filename(
                concept_name
            )
        )

        concept_path = (
            concepts_folder
            / f"{concept_filename}.md"
        )

        lines = [
            "---",
            "type: concept",
            f'concept_id: "{concept_id}"',
            f'concept: "{concept_name}"',
            "---",
            "",
            f"# {concept_name}",
            "",
        ]

        if parent_concept:
            parent_filename = (
                sanitize_filename(
                    parent_concept
                )
            )

            lines.extend(
                [
                    (
                        "**Parent Concept:** "
                        f"[[{parent_filename}|"
                        f"{parent_concept}]]"
                    ),
                    "",
                ]
            )

        lines.extend(
            [
                "## Books",
                "",
            ]
        )

        if data["books"]:
            for (
                book_note_name,
                book_title,
            ) in sorted(
                data["books"],
                key=lambda item:
                item[1].casefold(),
            ):
                lines.append(
                    f"- [[{book_note_name}|"
                    f"{book_title}]]"
                )
        else:
            lines.append(
                "_No books linked yet._"
            )

        lines.extend(
            [
                "",
                "## Passages",
                "",
            ]
        )

        if data["passages"]:
            sorted_passages = sorted(
                data["passages"],
                key=lambda item: (
                    item["book_title"]
                    .casefold(),
                    item["current_page"]
                    if item[
                        "current_page"
                    ] is not None
                    else 999999,
                ),
            )

            for passage in sorted_passages:
                location = ""

                if (
                    passage["current_page"]
                    is not None
                    and passage[
                        "total_pages"
                    ] is not None
                ):
                    location = (
                        f" "
                        f"({passage['current_page']}/"
                        f"{passage['total_pages']})"
                    )

                lines.append(
                    f"- [[{passage['note_name']}|"
                    f"{passage['chapter']}"
                    f"{location}]]"
                )
        else:
            lines.append(
                "_No passages linked yet._"
            )

        lines.extend(
            [
                "",
                "## Matched Terms",
                "",
            ]
        )

        if data["keywords"]:
            for keyword in sorted(
                data["keywords"],
                key=str.casefold,
            ):
                lines.append(
                    f"- {keyword}"
                )
        else:
            lines.append(
                "_No matched terms yet._"
            )

        lines.extend(
            [
                "",
                "## My Working Understanding",
                "",
                (
                    "_Add your own evolving "
                    "interpretation here._"
                ),
                "",
                "## AI Synthesis",
                "",
                "_To be generated later._",
                "",
                "## Related Concepts",
                "",
                "_To be generated later._",
                "",
            ]
        )

        concept_path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        print(
            f"Created concept page: "
            f"{concept_path}"
        )

    print("\n" + "=" * 60)
    print("CONCEPT EXPORT COMPLETE")
    print(
        f"Concept pages created: "
        f"{len(concept_catalogue)}"
    )


if __name__ == "__main__":
    export_concept_pages()