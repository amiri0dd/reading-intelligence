from pathlib import Path
import json


VAULT_PASSAGES_DIR = Path("vault/Passages")


def load_connections(
    path: str = "processed/connections.json",
) -> list[dict]:

    input_path = Path(path)

    if not input_path.exists():
        return []

    with input_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def connection_strength(
    similarity: float,
) -> str:

    if similarity >= 0.70:
        return "Strong"

    if similarity >= 0.60:
        return "Suggested"

    return "Weak"


def build_connection_line(
    other_note: str,
    other_book: str,
    similarity: float,
) -> str:

    strength = connection_strength(
        similarity
    )

    return (
        f"- [[{other_note}]] "
        f"({other_book}) "
        f"— {strength} semantic connection "
        f"({similarity:.3f})"
    )


def replace_connections_section(
    note_path: Path,
    lines: list[str],
) -> None:
    """
    Replace only the generated Connections section of
    an existing passage note.
    """

    if not note_path.exists():
        print(
            f"Warning: passage note not found: "
            f"{note_path}"
        )
        return

    text = note_path.read_text(
        encoding="utf-8"
    )

    heading = "## Connections"

    if heading in text:
        before = text.split(
            heading,
            1,
        )[0].rstrip()

        new_text = (
            before
            + "\n\n"
            + heading
            + "\n\n"
            + "\n".join(lines)
            + "\n"
        )

    else:
        new_text = (
            text.rstrip()
            + "\n\n"
            + heading
            + "\n\n"
            + "\n".join(lines)
            + "\n"
        )

    note_path.write_text(
        new_text,
        encoding="utf-8",
    )


def export_connections_to_obsidian(
    connections_path: str = (
        "processed/connections.json"
    ),
    minimum_similarity: float = 0.55,
) -> None:

    connections = load_connections(
        connections_path
    )

    note_connections = {}

    for connection in connections:

        score = connection[
            "similarity"
        ]

        if score < minimum_similarity:
            continue

        source_note = connection[
            "source_note"
        ]

        target_note = connection[
            "target_note"
        ]

        source_line = build_connection_line(
            other_note=target_note,
            other_book=connection[
                "target_book"
            ],
            similarity=score,
        )

        target_line = build_connection_line(
            other_note=source_note,
            other_book=connection[
                "source_book"
            ],
            similarity=score,
        )

        note_connections.setdefault(
            source_note,
            [],
        ).append(source_line)

        note_connections.setdefault(
            target_note,
            [],
        ).append(target_line)

    updated = 0

    for note_name, lines in note_connections.items():

        note_path = (
            VAULT_PASSAGES_DIR
            / f"{note_name}.md"
        )

        unique_lines = list(
            dict.fromkeys(lines)
        )

        replace_connections_section(
            note_path,
            unique_lines,
        )

        if note_path.exists():
            updated += 1

    print()
    print(
        f"Passage notes with semantic "
        f"connections: {updated}"
    )


if __name__ == "__main__":
    export_connections_to_obsidian()