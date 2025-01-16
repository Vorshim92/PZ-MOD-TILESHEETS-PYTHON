import sys
import subprocess
import os

# 1. Check if the PIL (Pillow) library is installed
try:
    from PIL import Image
except ImportError:
    print("The Pillow (PIL) library is not installed.")
    choice = input("Do you want to install it automatically? (Y/n): ").strip().lower()
    if choice in ("y", "yes", ""):
        try:
            # 2. Install Pillow using pip
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
            print("Pillow installed successfully!")

            # 3. Re-run the script itself (with the same arguments, if any)
            print("Restarting the script...")
            python = sys.executable  # Python executable in use
            script = sys.argv[0]     # the path to this script
            args = sys.argv[1:]      # any arguments passed to the script

            # Remember to import 'subprocess'
            subprocess.check_call([python, script] + args)
            sys.exit(0)

        except Exception as e:
            print(f"Error during Pillow installation: {e}")
            sys.exit(1)
    else:
        print("Installation canceled. Cannot proceed without Pillow.")
        sys.exit(1)

# At this point we know that Pillow is installed
# and we can import it safely
from PIL import Image

# If you want to use tkinter to select folders
try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    print("tkinter is not available, cannot show dialog windows.")
    sys.exit(1)


def create_tilesheet(
    input_folder,
    output_folder,
    output_filename="tilesheet.png",
    max_columns=8,
    tile_width=128,
    tile_height=256,
    dpi=96
):
    """ Example function that creates a tilesheet from a set of images. """
    import math  # Local import, if you prefer

    # 1. Read all image files
    images = [
        f for f in os.listdir(input_folder)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]
    images.sort()

    if not images:
        print("No images found in the input folder.")
        return

    # 2. Calculate columns and rows
    num_images = len(images)
    columns = min(num_images, max_columns)
    rows = math.ceil(num_images / columns)

    # 3. Total size
    grid_width = columns * tile_width
    grid_height = rows * tile_height

    # 4. Create the final image
    grid_image = Image.new('RGBA', (grid_width, grid_height), (0, 0, 0, 0))

    # 5. Paste each image
    for i, img_file in enumerate(images):
        img_path = os.path.join(input_folder, img_file)
        with Image.open(img_path) as im:
            # Resize if it doesn't match
            if im.size != (tile_width, tile_height):
                im = im.resize((tile_width, tile_height), Image.Resampling.LANCZOS)

            col = i % columns
            row = i // columns
            x = col * tile_width
            y = row * tile_height
            grid_image.paste(im, (x, y))

    # 6. Save the result
    output_path = os.path.join(output_folder, output_filename)
    grid_image.save(output_path, dpi=(dpi, dpi))
    print(f"Tilesheet saved in: {output_path} (DPI={dpi})")


def main():
    # Create a small invisible tkinter window
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

    create_tilesheet(
        input_folder=input_folder,
        output_folder=output_folder,
        output_filename="tilesheet.png",
        max_columns=8,
        tile_width=128,
        tile_height=256,
        dpi=96
    )

if __name__ == "__main__":
    main()
