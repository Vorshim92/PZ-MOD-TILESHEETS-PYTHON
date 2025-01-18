import sys
import subprocess
import os
import re
import math

# 1. Check if the PIL (Pillow) library is installed
try:
    from PIL import Image
except ImportError:
    print("The Pillow (PIL) library is not installed.")
    choice = input("Do you want to install it automatically? (Y/n): ").strip().lower()
    if choice in ("y", "yes", ""):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
            print("Pillow installed successfully!\nRestarting the script...")
            python = sys.executable
            script = sys.argv[0]
            args = sys.argv[1:]
            subprocess.check_call([python, script] + args)
            sys.exit(0)
        except Exception as e:
            print(f"Error during Pillow installation: {e}")
            sys.exit(1)
    else:
        print("Installation canceled. Cannot proceed without Pillow.")
        sys.exit(1)

try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    print("tkinter is not available, cannot show dialog windows.")
    sys.exit(1)

def natural_key(filename):
    """
    Splits the string into blocks of characters and numbers:
    e.g. "camping_04_10.png" -> ["camping_","_","04","_","10",".png"]
    Then converts the numeric blocks to integers for natural sorting.
    """
    return [
        int(token) if token.isdigit() else token
        for token in re.split(r'(\d+)', filename)
    ]

def parse_last_number(filename):
    """
    Extracts the LAST number (integer) present in the filename.
    Example: "camping_04_12.png" -> 12
             "camping_04_0.png"  -> 0
    If no numbers are found, returns None.
    """
    tokens = re.split(r'(\d+)', filename)
    numbers = [int(t) for t in tokens if t.isdigit()]
    if not numbers:
        return None
    return numbers[-1]  # Last number found

def create_tilesheet(
    input_folder,
    output_folder,
    output_filename="tilesheet.png",
    max_columns=8,
    tile_width=128,
    tile_height=256,
    dpi=96,
    fill_missing_indices=False
):
    """
    Creates a tilesheet from all image files in 'input_folder',
    sorting them naturally and distributing them in a grid with
    'max_columns' columns.

    If fill_missing_indices=True, fills gaps in numeric indices
    with empty tiles. Otherwise, uses only existing files.
    """

    # 1. Retrieve PNG/JPG/JPEG files
    all_files = [
        f for f in os.listdir(input_folder)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]
    if not all_files:
        print("No images found in the input folder.")
        return

    # 2. Natural order
    all_files.sort(key=natural_key)

    if not fill_missing_indices:
        # --- MODE WITHOUT PLACEHOLDERS ---
        # Simply use the sorted list as is
        expanded_files = all_files
    else:
        # --- MODE WITH PLACEHOLDERS ---
        # Create a dictionary: index -> file
        index_to_file = {}
        valid_indices = []

        for f in all_files:
            idx = parse_last_number(f)
            if idx is not None:
                index_to_file[idx] = f
                valid_indices.append(idx)
            else:
                print(f"Warning: the file {f} does not contain numbers, ignored.")

        if not valid_indices:
            print("No files with numbers found, cannot create placeholders.")
            return

        min_idx = min(valid_indices)
        max_idx = max(valid_indices)

        expanded_files = []
        # Insert None (placeholder) where an index is missing
        for i in range(min_idx, max_idx + 1):
            if i in index_to_file:
                expanded_files.append(index_to_file[i])
            else:
                expanded_files.append(None)

    # 3. Calculate columns and rows
    num_images = len(expanded_files)
    columns = min(num_images, max_columns)
    rows = math.ceil(num_images / columns)

    # 4. Create the final "grid" image
    grid_width = columns * tile_width
    grid_height = rows * tile_height
    grid_image = Image.new('RGBA', (grid_width, grid_height), (0, 0, 0, 0))

    # 5. Paste each image or, if None, an empty tile
    for i, maybe_file in enumerate(expanded_files):
        col = i % columns
        row = i // columns
        x = col * tile_width
        y = row * tile_height

        if maybe_file is None:
            # If fill_missing_indices and maybe_file == None, create an empty tile
            empty_tile = Image.new('RGBA', (tile_width, tile_height), (0, 0, 0, 0))
            grid_image.paste(empty_tile, (x, y))
        else:
            img_path = os.path.join(input_folder, maybe_file)
            with Image.open(img_path) as im:
                if im.size != (tile_width, tile_height):
                    im = im.resize((tile_width, tile_height), Image.Resampling.LANCZOS)
                grid_image.paste(im, (x, y))

    # 6. Save the result
    output_path = os.path.join(output_folder, output_filename)
    grid_image.save(output_path, dpi=(dpi, dpi))
    print(f"\nTilesheet saved in: {output_path}")
    print(f"Dimensions: {grid_width}x{grid_height} px @ {dpi} DPI")
    if fill_missing_indices:
        print("Mode: with placeholders for missing indices.")
    else:
        print("Mode: without placeholders (only existing images).")

def main():
    # Hidden tkinter window
    root = tk.Tk()
    root.withdraw()

    print("Select the input folder:")
    input_folder = filedialog.askdirectory()
    if not input_folder:
        print("No input folder selected, exiting.")
        return

    print("Select the output folder:")
    output_folder = filedialog.askdirectory()
    if not output_folder:
        print("No output folder selected, exiting.")
        return

    # Ask the user whether to create empty images for missing indices
    choice = input("Do you want to create empty images (placeholders) for missing indices? (Y/n): ").strip().lower()
    fill_missing = (choice in ("y", "yes", ""))  # True if 'y' or enter, False if 'n'

    create_tilesheet(
        input_folder=input_folder,
        output_folder=output_folder,
        output_filename="tilesheet.png",
        max_columns=8,
        tile_width=128,
        tile_height=256,
        dpi=96,
        fill_missing_indices=fill_missing
    )

if __name__ == "__main__":
    main()
