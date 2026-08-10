from pathlib import Path

import pandas as pd


def load_concept_catalogue(
    catalogue_path: str = "config/concepts.csv",
) -> pd.DataFrame:
    """
    Load the controlled concept vocabulary.
    """

    catalogue_file = Path(catalogue_path)

    if not catalogue_file.exists():
        raise FileNotFoundError(
            f"Could not find concept catalogue: {catalogue_file}"
        )

    concepts = pd.read_csv(catalogue_file)

    required_columns = {
        "concept_id",
        "concept_name",
        "parent_concept",
        "keywords",
    }

    missing_columns = required_columns - set(concepts.columns)

    if missing_columns:
        raise ValueError(
            "Concept catalogue is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    for column in required_columns:
        concepts[column] = (
            concepts[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    return concepts


if __name__ == "__main__":
    concepts = load_concept_catalogue()

    print("CONCEPT CATALOGUE")
    print("=" * 60)

    for _, concept in concepts.iterrows():
        print(
            f"{concept['concept_id']} | "
            f"{concept['concept_name']} | "
            f"{concept['parent_concept']}"
        )