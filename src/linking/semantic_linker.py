import json
from pathlib import Path

from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


def load_processed_records(
    processed_folder: str = "processed",
) -> list[dict]:
    """
    Load all processed screenshot JSON records.
    """

    folder = Path(processed_folder)

    if not folder.exists():
        raise FileNotFoundError(
            f"Could not find processed folder: {folder}"
        )

    records = []

    for json_file in sorted(folder.glob("*.json")):
        with json_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            record = json.load(file)

        record["_json_file"] = str(json_file)

        records.append(record)

    return records


def build_passage_text(record: dict) -> str:
    """
    Build the text representation used for semantic comparison.

    We combine the chapter title and passage body so the embedding
    has some contextual information.
    """

    chapter = record.get("chapter") or ""
    body = record.get("body_text") or ""

    return f"{chapter}\n\n{body}".strip()


def find_semantic_connections(
    processed_folder: str = "processed",
    minimum_similarity: float = 0.55,
    max_connections_per_passage: int = 3,
    cross_book_only: bool = True,
) -> list[dict]:
    """
    Find semantically related passages.

    Parameters
    ----------
    processed_folder:
        Folder containing JSON records.

    minimum_similarity:
        Minimum similarity score required for a connection.

    max_connections_per_passage:
        Maximum number of suggestions generated for each passage.

    cross_book_only:
        If True, only connect passages from different books.
    """

    records = load_processed_records(
        processed_folder
    )

    if len(records) < 2:
        print(
            "Need at least two processed passages "
            "to calculate semantic connections."
        )
        return []

    texts = [
        build_passage_text(record)
        for record in records
    ]

    print(
        f"Loading semantic model: {MODEL_NAME}"
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    print(
        f"Encoding {len(texts)} passages..."
    )

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    # Because embeddings are normalized, matrix multiplication
    # gives cosine similarity.
    similarity_matrix = (
        embeddings @ embeddings.T
    )

    connections = []

    for source_index, source_record in enumerate(records):

        candidates = []

        for target_index, target_record in enumerate(records):

            # Never compare a passage with itself.
            if source_index == target_index:
                continue

            # Optional: only discover cross-book relationships.
            if (
                cross_book_only
                and source_record.get("book_id")
                == target_record.get("book_id")
            ):
                continue

            score = float(
                similarity_matrix[
                    source_index,
                    target_index
                ]
            )

            if score < minimum_similarity:
                continue

            candidates.append(
                {
                    "target_index": target_index,
                    "similarity": score,
                }
            )

        candidates.sort(
            key=lambda item: item["similarity"],
            reverse=True,
        )

        candidates = candidates[
            :max_connections_per_passage
        ]

        for candidate in candidates:
            target_record = records[
                candidate["target_index"]
            ]

            connection = {
                "source_image": Path(
                    source_record["original_image"]
                ).name,
                "source_book_id": source_record.get(
                    "book_id"
                ),
                "source_book": source_record.get(
                    "book_title"
                ),
                "source_chapter": source_record.get(
                    "chapter"
                ),

                "target_image": Path(
                    target_record["original_image"]
                ).name,
                "target_book_id": target_record.get(
                    "book_id"
                ),
                "target_book": target_record.get(
                    "book_title"
                ),
                "target_chapter": target_record.get(
                    "chapter"
                ),

                "similarity": round(
                    candidate["similarity"],
                    3,
                ),
                "relationship_type": (
                    "semantic_similarity"
                ),
            }

            connections.append(
                connection
            )

    return connections


def save_connections(
    connections: list[dict],
    output_path: str = "processed/connections.json",
) -> Path:
    """
    Save semantic relationships to JSON.
    """

    output_file = Path(output_path)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            connections,
            file,
            ensure_ascii=False,
            indent=4,
        )

    print(
        f"Saved semantic connections: {output_file}"
    )

    return output_file


if __name__ == "__main__":
    connections = find_semantic_connections()

    print("\nSEMANTIC CONNECTIONS")
    print("=" * 60)

    for connection in connections:
        print()
        print(
            f"{connection['source_book']} "
            f"→ {connection['target_book']}"
        )
        print(
            f"{connection['source_chapter']} "
            f"→ {connection['target_chapter']}"
        )
        print(
            f"Similarity: "
            f"{connection['similarity']}"
        )

    save_connections(
        connections
    )