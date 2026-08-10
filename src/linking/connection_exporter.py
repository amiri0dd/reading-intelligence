import json
from pathlib import Path

from src.export.markdown_exporter import sanitize_filename


def load_connections(
    connections_path: str = "processed/connections.json",
) -> list[dict]:
    """
    Load semantic connections from JSON.
    """

    path = Path(connections_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Could not find connections file: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def deduplicate_connections(
    connections: list[dict],
) -> list[dict]:
    """
    Remove reciprocal duplicates such as:

    A -> B
    B -> A

    keeping only one copy of each pair.
    """

    unique = []
    seen_pairs = set()

    for connection in connections:
        source = connection["source_image"]
        target = connection["target_image"]

        pair_key = tuple(sorted([source, target]))

        if pair_key in seen_pairs:
            continue

        seen_pairs.add(pair_key)
        unique.append(connection)

    return unique


def build_passage_note_name(
    book_title: str,
    chapter: str,
    image_name: str,
) -> str:
    """
    Reconstruct the passage note filename used by
    markdown_exporter.py.
    """

    image_stem = Path(image_name).stem

    return sanitize_filename(
        f"{book_title} - {chapter} - {image_stem}"
    )


def classify_strength(score: float) -> str:
    """
    Human-readable relationship strength.
    """

    if score >= 0.70:
        return "Strong"

    if score >= 0.60:
        return "Suggested"

    return "Weak"


def build_connection_map(
    connections: list[dict],
    minimum_similarity: float = 0.60,
) -> dict[str, list[dict]]:
    """
    Convert connection pairs into a mapping where
    each passage receives links to its related passages.

    A single stored A-B relationship is written into
    both passage A and passage B.
    """

    connection_map = {}

    for connection in connections:
        score = float(connection["similarity"])

        if score < minimum_similarity:
            continue

        source_note = build_passage_note_name(
            connection["source_book"],
            connection["source_chapter"],
            connection["source_image"],
        )

        target_note = build_passage_note_name(
            connection["target_book"],
            connection["target_chapter"],
            connection["target_image"],
        )

        strength = classify_strength(score)

        source_entry = {
            "note_name": target_note,
            "book": connection["target_book"],
            "chapter": connection["target_chapter"],
            "similarity": score,
            "strength": strength,
        }

        target_entry = {
            "note_name": source_note,
            "book": connection["source_book"],
            "chapter": connection["source_chapter"],
            "similarity": score,
            "strength": strength,
        }

        connection_map.setdefault(
            source_note,
            []
        ).append(source_entry)

        connection_map.setdefault(
            target_note,
            []
        ).append(target_entry)

    return connection_map


def format_connections(
    connections: list[dict],
) -> str:
    """
    Convert related passages into Obsidian Markdown.
    """

    if not connections:
        return "_No strong cross-book connections detected yet._"

    connections = sorted(
        connections,
        key=lambda item: item["similarity"],
        reverse=True,
    )

    lines = []

    for connection in connections:
        lines.append(
            f"- [[{connection['note_name']}|"
            f"{connection['book']} — "
            f"{connection['chapter']}]]"
        )

        lines.append(
            f"  - {connection['strength']} semantic connection "
            f"({connection['similarity']:.3f})"
        )

    return "\n".join(lines)


def replace_connections_section(
    note_text: str,
    new_connections: str,
) -> str:
    """
    Replace the generated ## Connections section
    without altering the rest of the passage note.
    """

    heading = "## Connections"

    if heading not in note_text:
        return (
            note_text.rstrip()
            + "\n\n"
            + heading
            + "\n\n"
            + new_connections
            + "\n"
        )

    before, after = note_text.split(
        heading,
        maxsplit=1,
    )

    # Find the next level-2 heading after Connections.
    next_heading_index = after.find("\n## ")

    if next_heading_index == -1:
        return (
            before
            + heading
            + "\n\n"
            + new_connections
            + "\n"
        )

    remaining = after[next_heading_index:]

    return (
        before
        + heading
        + "\n\n"
        + new_connections
        + remaining
    )


def export_connections_to_obsidian(
    connections_path: str = "processed/connections.json",
    vault_path: str = "vault",
    minimum_similarity: float = 0.60,
) -> None:
    """
    Write filtered semantic connections into
    Obsidian passage notes.
    """

    connections = load_connections(
        connections_path
    )

    deduplicated = deduplicate_connections(
        connections
    )

    connection_map = build_connection_map(
        deduplicated,
        minimum_similarity=minimum_similarity,
    )

    passages_folder = (
        Path(vault_path)
        / "Passages"
    )

    if not passages_folder.exists():
        raise FileNotFoundError(
            f"Could not find passage folder: {passages_folder}"
        )

    updated = 0
    missing = []

    for note_name, related in connection_map.items():
        note_path = (
            passages_folder
            / f"{note_name}.md"
        )

        if not note_path.exists():
            missing.append(note_name)
            continue

        note_text = note_path.read_text(
            encoding="utf-8"
        )

        connections_markdown = format_connections(
            related
        )

        updated_text = replace_connections_section(
            note_text,
            connections_markdown,
        )

        note_path.write_text(
            updated_text,
            encoding="utf-8"
        )

        updated += 1

        print(
            f"Updated connections: {note_path.name}"
        )

    print("\n" + "=" * 60)
    print("CONNECTION EXPORT COMPLETE")
    print(
        f"Original connections: {len(connections)}"
    )
    print(
        f"After reciprocal deduplication: "
        f"{len(deduplicated)}"
    )
    print(
        f"Passage notes updated: {updated}"
    )
    print(
        f"Missing passage notes: {len(missing)}"
    )

    if missing:
        print("\nMISSING NOTES")
        print("=" * 60)

        for note_name in missing:
            print(note_name)


if __name__ == "__main__":
    export_connections_to_obsidian(
        minimum_similarity=0.60
    )