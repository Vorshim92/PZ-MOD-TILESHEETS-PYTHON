import sys
import subprocess
import os
import re

###############################################################################
# 1. Check if the PIL (Pillow) library is installed and, if not, propose      #
#    installation and restart the script.                                     #
###############################################################################
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

###############################################################################
# If we get here, Pillow is installed and we can import it.                   #
###############################################################################
from PIL import Image

# Try to import tkinter to show dialog windows
try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    print("tkinter is not available, cannot show dialog windows.")
    sys.exit(1)

###############################################################################
# Support functions                                                           #
###############################################################################
def parse_last_number(filename: str):
    """
    Extracts the LAST number (integer) present in the file name.
    Examples:
      "camping_04_12.png" -> 12
      "camping_04_0.png"  -> 0
      "tenda10.jpg"       -> 10
    If no numbers are found, returns None.
    """
    tokens = re.split(r'(\d+)', filename)  # Split into text / number blocks
    numbers = [int(t) for t in tokens if t.isdigit()]
    if not numbers:
        return None
    return numbers[-1]  # Last number found

def parse_prefix(filename: str, last_number: int) -> str:
    """
    Derives the prefix of the file by REMOVING the final numeric part (and the extension).
    Example:
      filename = "camping_04_12.png"
      last_number = 12
      -> prefix = "camping_04_"
    """
    # Remove the extension
    base, _ext = os.path.splitext(filename)  # "camping_04_12" , ".png"
    # Convert last_number to string
    num_str = str(last_number)
    # If base ends with that num_str, remove those characters
    if base.endswith(num_str):
        prefix = base[: -len(num_str)]
    else:
        prefix = base  # In case of mismatch (rare)
    return prefix

###############################################################################
# Main function: generates missing files                                      #
###############################################################################
def generate_missing_images(
    folder: str,
    tile_width=128,
    tile_height=256,
    dpi=96
):
    """
    Searches the 'folder' for all images with .png/.jpg/.jpeg extensions
    and extracts the final numeric index. If there are "holes" in the indices, creates
    empty images (128x256 at 96 DPI) with names corresponding to the original scheme.

    Example:
      In the folder you have:
        camping_04_0.png
        camping_04_4.png
      Will create:
        camping_04_1.png
        camping_04_2.png
        camping_04_3.png
      as empty images (white or transparent, your choice).
    """

    # 1. List files
    all_files = [
        f for f in os.listdir(folder)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]
    if not all_files:
        print("No images found in the selected folder!")
        return

    # 2. Extract indices (last number) and create a dict { index : filename }
    index_to_file = {}
    for filename in all_files:
        idx = parse_last_number(filename)
        if idx is not None:
            # Map the index to the filename
            index_to_file[idx] = filename

    if not index_to_file:
        print("None of the images contain a number in the name. Exiting.")
        return

    # 3. Find the min..max range
    all_indices = list(index_to_file.keys())
    min_idx = min(all_indices)
    max_idx = max(all_indices)

    # 4. Deduce the "prefix" from the FIRST file found (or from min_idx)
    #    Assume that ALL files in the folder have the same prefix
    example_file = index_to_file[min_idx]
    prefix = parse_prefix(example_file, min_idx)
    # Final extension: check the one from the example file
    _base, ext = os.path.splitext(example_file)
    ext = ext.lower()  # e.g. ".png"

    # 5. Iterate from min_idx to max_idx and look for "missing"
    missing_indices = []
    for i in range(min_idx, max_idx + 1):
        if i not in index_to_file:
            missing_indices.append(i)

    if not missing_indices:
        print(f"There are no 'holes' in the indices between {min_idx} and {max_idx}.")
        return

    print(f"I will create {len(missing_indices)} missing images: {missing_indices}")

    # 6. Generate an empty image (in memory) and save it with the appropriate name
    #    If you prefer transparent, use RGBA and a color (0,0,0,0).
    #    If you prefer white, use RGB (255,255,255).
    #    Here we use a transparent background:
    for idx in missing_indices:
        new_file_name = f"{prefix}{idx}{ext}"  # Example: "camping_04_{1}.png"
        new_file_path = os.path.join(folder, new_file_name)

        # Create 128x256 transparent image
        empty_img = Image.new("RGBA", (tile_width, tile_height), (0, 0, 0, 0))
        # If you prefer white, you can do:
        # empty_img = Image.new("RGB", (tile_width, tile_height), (255, 255, 255))

        # Save with the requested DPI
        empty_img.save(new_file_path, dpi=(dpi, dpi))

        print(f"Created: {new_file_name}  ({tile_width}x{tile_height} @ {dpi} DPI)")

    print("Operation completed!")


###############################################################################
# main(): asks the user for a folder and generates the missing files          #
###############################################################################
def main():
    root = tk.Tk()
    root.withdraw()

    print("Select the folder with the input images:")
    input_folder = filedialog.askdirectory()
    if not input_folder:
        print("No folder selected. Exiting.")
        return

    generate_missing_images(
        folder=input_folder,
        tile_width=128,
        tile_height=256,
        dpi=96
    )

if __name__ == "__main__":
    main()
