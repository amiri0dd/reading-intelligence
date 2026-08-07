from pathlib import Path
from PIL import Image


def convert_bmp_to_png(input_path: str, output_path: str | None = None) -> Path:
    """
    Open a BMP image, report its basic properties,
    and save a PNG copy.

    Parameters
    ----------
    input_path:
        Path to the original BMP screenshot.

    output_path:
        Optional destination for the PNG.
        If omitted, the PNG is saved beside the BMP.

    Returns
    -------
    Path
        The path to the newly created PNG file.
    """

    input_file = Path(input_path)

    # Make sure the screenshot actually exists.
    if not input_file.exists():
        raise FileNotFoundError(f"Could not find: {input_file}")

    # Make sure we're receiving a BMP file.
    if input_file.suffix.lower() != ".bmp":
        raise ValueError(f"Expected a .bmp file, received: {input_file.suffix}")

    # Decide where the PNG should be saved.
    if output_path is None:
        output_file = input_file.with_suffix(".png")
    else:
        output_file = Path(output_path)

    # Create the destination folder if necessary.
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Open the screenshot.
    with Image.open(input_file) as image:
        print("Reading screenshot...")
        print(f"File: {input_file.name}")
        print(f"Format: {image.format}")
        print(f"Dimensions: {image.width} x {image.height}")
        print(f"Mode: {image.mode}")

        # Save a PNG copy.
        image.save(output_file, format="PNG")

    print()
    print("Successfully converted.")
    print(f"Output: {output_file}")

    return output_file
if __name__ == "__main__":
    convert_bmp_to_png("sample_data/sample_page.bmp")