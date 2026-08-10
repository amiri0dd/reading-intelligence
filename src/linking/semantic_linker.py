from pathlib import Path
import json
import re

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


def sanitize_filename(name: str) -> str:
    """
    Match the filename sanitization used by the Obsidian exporters.
    """
    name = re.sub(r'[<>:"/\\|?*]', "-", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()


def build_screenshot_note_name(record: dict) -> str:
    """
    Reconstruct the Obsidian note name for an Xteink passage.
    """

    chapter = record.get("chapter") or "Unknown Chapter"

    current_page = record.get("current_page")
    total_pages = record.get("total_pages")

    if current_page is not None and total_pages is not None:
        name = f"{chapter} ({current_page}/{total_pages})"
    else:
        name = chapter

    return sanitize_filename(name)


def build_typed_note_name(record: dict) -> str:
    """
    Reconstruct the Obsidian note name for a typed book passage.
    """

    return sanitize_filename(
        f"{record['book_title']} - {record['record_id']}"
    )


def normalize_screenshot_record(record: dict) -> dict | None:
    """
    Normalize an Xteink screenshot record for semantic comparison.
    """

    text = record.get("body_text", "").strip()

    if not text:
        return None

    chapter = record.get("chapter", "")

    semantic_text = "\n".join(
        part
        for part in [
            chapter,
            text,
        ]
        if part
    )

    original_image = record.get(
        "original_image",
        ""
    )

    passage_id = (
        Path(original_image).stem
        if original_image
        else record.get("png_image", "unknown")
    )

    return {
        "passage_id": passage_id,
        "source_kind": "xteink",
        "book_id": record.get("book_id"),
        "book_title": record.get("book_title"),
        "author": record.get("author"),
        "chapter": chapter,
        "content_type": "book_quote",
        "provenance": "book",
        "text": text,
        "semantic_text": semantic_text,
        "note_name": build_screenshot_note_name(record),
    }


def normalize_typed_record(record: dict) -> dict | None:
    """
    Normalize a typed passage record.

    For v1 semantic linking, only actual book quotations
    participate in passage-to-passage similarity.
    """

    if record.get("content_type") != "book_quote":
        return None

    text = record.get("text", "").strip()

    if not text:
        return None

    return {
        "passage_id": record.get("record_id"),
        "source_kind": "typed_document",
        "book_id": record.get("book_id"),
        "book_title": record.get("book_title"),
        "author": record.get("author"),
        "chapter": "",
        "content_type": record.get("content_type"),
        "provenance": record.get("provenance"),
        "text": text,
        "semantic_text": text,
        "note_name": build_typed_note_name(record),
    }


def load_semantic_records(
    processed_path: str = "processed",
) -> list[dict]:
    """
    Load Xteink and typed passage JSON records.
    """

    root = Path(processed_path)

    records = []

    # --------------------------------------------------
    # Xteink screenshot records
    # --------------------------------------------------

    for json_file in root.glob("*.json"):

        if json_file.name == "connections.json":
            continue

        try:
            with json_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                raw = json.load(file)

        except (json.JSONDecodeError, OSError):
            continue

        if not isinstance(raw, dict):
            continue

        normalized = normalize_screenshot_record(raw)

        if normalized:
            records.append(normalized)

    # --------------------------------------------------
    # Typed-document records
    # --------------------------------------------------

    typed_directory = root / "typed_notes"

    if typed_directory.exists():

        for json_file in typed_directory.glob("*.json"):

            try:
                with json_file.open(
                    "r",
                    encoding="utf-8",
                ) as file:
                    raw = json.load(file)

            except (json.JSONDecodeError, OSError):
                continue

            if not isinstance(raw, dict):
                continue

            normalized = normalize_typed_record(raw)

            if normalized:
                records.append(normalized)

    return records


def find_semantic_connections(
    processed_path: str = "processed",
    minimum_similarity: float = 0.55,
    max_connections_per_passage: int = 3,
    cross_book_only: bool = True,
) -> list[dict]:
    """
    Find semantic passage relationships across the entire
    reading library.

    Reciprocal duplicates are prevented automatically.
    """

    records = load_semantic_records(
        processed_path
    )

    if len(records) < 2:
        print(
            "Not enough passage records for semantic linking."
        )
        return []

    print()
    print("=" * 70)
    print("SEMANTIC LINKING")
    print("=" * 70)

    print(
        f"Passages available: {len(records)}"
    )

    screenshot_count = sum(
        record["source_kind"] == "xteink"
        for record in records
    )

    typed_count = sum(
        record["source_kind"] == "typed_document"
        for record in records
    )

    print(
        f"Xteink passages: {screenshot_count}"
    )

    print(
        f"Typed passages: {typed_count}"
    )

    print(
        f"Minimum similarity: {minimum_similarity}"
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    texts = [
        record["semantic_text"]
        for record in records
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    similarity_matrix = (
        embeddings @ embeddings.T
    )

    connections = []

    seen_pairs = set()

    for source_index, source in enumerate(records):

        candidates = []

        for target_index, target in enumerate(records):

            if source_index == target_index:
                continue

            if (
                cross_book_only
                and source["book_id"]
                == target["book_id"]
            ):
                continue

            score = float(
                similarity_matrix[
                    source_index,
                    target_index,
                ]
            )

            if score < minimum_similarity:
                continue

            candidates.append(
                (
                    target_index,
                    score,
                )
            )

        candidates.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        candidates = candidates[
            :max_connections_per_passage
        ]

        for target_index, score in candidates:

            target = records[target_index]

            pair_key = tuple(
                sorted(
                    [
                        (
                            source["source_kind"],
                            str(source["passage_id"]),
                        ),
                        (
                            target["source_kind"],
                            str(target["passage_id"]),
                        ),
                    ]
                )
            )

            if pair_key in seen_pairs:
                continue

            seen_pairs.add(pair_key)

            connections.append(
                {
                    "source_id": source[
                        "passage_id"
                    ],
                    "source_kind": source[
                        "source_kind"
                    ],
                    "source_book_id": source[
                        "book_id"
                    ],
                    "source_book": source[
                        "book_title"
                    ],
                    "source_chapter": source[
                        "chapter"
                    ],
                    "source_note": source[
                        "note_name"
                    ],
                    "target_id": target[
                        "passage_id"
                    ],
                    "target_kind": target[
                        "source_kind"
                    ],
                    "target_book_id": target[
                        "book_id"
                    ],
                    "target_book": target[
                        "book_title"
                    ],
                    "target_chapter": target[
                        "chapter"
                    ],
                    "target_note": target[
                        "note_name"
                    ],
                    "similarity": round(
                        score,
                        3,
                    ),
                    "relationship_type":
                        "semantic_similarity",
                }
            )

    connections.sort(
        key=lambda connection:
            connection["similarity"],
        reverse=True,
    )

    print(
        f"Semantic connections found: "
        f"{len(connections)}"
    )

    return connections


def save_connections(
    connections: list[dict],
    output_path: str = (
        "processed/connections.json"
    ),
) -> Path:
    """
    Save semantic connections as JSON.
    """

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            connections,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Saved semantic connections: {path}"
    )

    return path


if __name__ == "__main__":

    connections = find_semantic_connections(
        minimum_similarity=0.55,
        max_connections_per_passage=3,
        cross_book_only=True,
    )

    save_connections(
        connections
    )