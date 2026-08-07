from pathlib import Path

import pandas as pd


def load_book_catalogue(
    catalogue_path: str = "config/books.csv"
) -> pd.DataFrame:
    """
    Load the master book catalogue from CSV.

    Parameters
    ----------
    catalogue_path:
        Path to books.csv.

    Returns
    -------
    pandas.DataFrame
        Validated book catalogue.
    """

    catalogue_file = Path(catalogue_path)

    if not catalogue_file.exists():
        raise FileNotFoundError(
            f"Could not find book catalogue: {catalogue_file}"
        )

    catalogue = pd.read_csv(catalogue_file)

    required_columns = {
        "book_id",
        "title",
        "author",
        "language",
        "status",
        "source_type",
        "keywords",
    }

    missing_columns = required_columns - set(catalogue.columns)

    if missing_columns:
        raise ValueError(
            "Book catalogue is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    # Clean common text fields.
    text_columns = [
        "book_id",
        "title",
        "author",
        "language",
        "status",
        "source_type",
        "keywords",
    ]

    for column in text_columns:
        catalogue[column] = (
            catalogue[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # Prevent duplicate book IDs.
    if catalogue["book_id"].duplicated().any():
        duplicates = catalogue.loc[
            catalogue["book_id"].duplicated(),
            "book_id"
        ].tolist()

        raise ValueError(
            f"Duplicate book_id values found: {duplicates}"
        )

    return catalogue


def get_book_by_id(
    book_id: str,
    catalogue_path: str = "config/books.csv",
) -> dict | None:
    """
    Return one book from the catalogue by book_id.
    """

    catalogue = load_book_catalogue(catalogue_path)

    match = catalogue[
        catalogue["book_id"].str.casefold()
        == book_id.strip().casefold()
    ]

    if match.empty:
        return None

    return match.iloc[0].to_dict()


if __name__ == "__main__":
    books = load_book_catalogue()

    print("BOOK CATALOGUE")
    print("=" * 60)

    for _, book in books.iterrows():
        print(
            f"{book['book_id']} | "
            f"{book['title']} | "
            f"{book['author']}"
        )