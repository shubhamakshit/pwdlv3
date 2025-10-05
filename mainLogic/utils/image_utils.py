import base64
import io
import math
import os
import shutil

import requests
from PIL import Image, ImageDraw, ImageFont

# --- Helper Function for Font Management ---
def get_or_download_font(font_path="arial.ttf", font_size=50):
    """
    Gets the Arial font, downloading it if necessary.

    Args:
        font_path (str): Path to save/load the font
        font_size (int): Font size to use

    Returns:
        ImageFont: The loaded font object
    """
    if not os.path.exists(font_path):
        print(f"Arial font not found locally. Downloading...")
        try:
            response = requests.get(
                "https://github.com/kavin808/arial.ttf/raw/refs/heads/master/arial.ttf",
                timeout=30
            )
            response.raise_for_status()

            with open(font_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Successfully downloaded Arial font to {font_path}")
        except Exception as e:
            print(f"Failed to download Arial font: {e}")
            print("Using default font instead.")
            return ImageFont.load_default()

    try:
        return ImageFont.truetype(font_path, size=font_size)
    except IOError:
        print("Error loading Arial font. Using default font.")
        return ImageFont.load_default()


def create_a4_pdf_from_images(image_info, base_folder, output_filename, images_per_page, orientation='portrait', grid_rows=None, grid_cols=None):
    if not image_info: return False
    A4_WIDTH_PX, A4_HEIGHT_PX = 4960, 7016
    font_large, font_small = get_or_download_font(font_size=60), get_or_download_font(font_size=50)
    pages, info_chunks = [], [image_info[i:i + images_per_page] for i in range(0, len(image_info), images_per_page)]
    for chunk in info_chunks:
        page_width, page_height = (A4_HEIGHT_PX, A4_WIDTH_PX) if orientation == 'landscape' else (A4_WIDTH_PX, A4_HEIGHT_PX)
        page = Image.new('RGB', (page_width, page_height), 'white')
        draw = ImageDraw.Draw(page)
        
        if grid_rows and grid_cols:
            rows, cols = grid_rows, grid_cols
        else:
            # Determine grid size based on images_per_page for consistent layout
            if images_per_page == 1:
                rows, cols = 1, 1
            elif images_per_page == 2:
                rows, cols = 2, 1
            elif images_per_page <= 4:
                rows, cols = 2, 2
            elif images_per_page <= 6:
                rows, cols = 3, 2
            elif images_per_page <= 9:
                rows, cols = 3, 3
            else:
                # Default for larger numbers, ensuring a grid-like structure
                side = int(math.ceil(math.sqrt(images_per_page)))
                rows, cols = side, side
        
        cell_width, cell_height = (page_width - 400) // cols, (page_height - 400) // rows
        for i, info in enumerate(chunk):
            col, row = i % cols, i // cols
            cell_x, cell_y = 200 + col * cell_width, 200 + row * cell_height
            try:
                img = None
                if info.get('image_data'):
                    # Handle base64 encoded image data
                    header, encoded = info['image_data'].split(",", 1)
                    image_data = base64.b64decode(encoded)
                    img = Image.open(io.BytesIO(image_data)).convert("RGB")
                elif info.get('processed_filename') or info.get('filename'):
                    # Handle image from file path
                    img_path = os.path.join(base_folder, info.get('processed_filename') or info.get('filename'))
                    img = Image.open(img_path).convert("RGB")

                if img:
                    target_w, target_h = cell_width - 40, cell_height - 170
                    
                    # Calculate new dimensions while maintaining aspect ratio
                    img_ratio = img.width / img.height
                    target_ratio = target_w / target_h
                    
                    if img_ratio > target_ratio:
                        # Image is wider than target area, scale by width
                        new_w = target_w
                        new_h = int(new_w / img_ratio)
                    else:
                        # Image is taller than target area, scale by height
                        new_h = target_h
                        new_w = int(new_h * img_ratio)

                    print(f"Original image size: {img.width}x{img.height}, Resized to: {new_w}x{new_h}")
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    
                    page.paste(img, (cell_x + 20, cell_y + 150))

                draw.text((cell_x + 20, cell_y + 20), f"Q: {info['question_number']}", fill="black", font=font_large)
                info_text = f"Status: {info['status']} | Marked: {info['marked_solution']} | Correct: {info['actual_solution']}"
                draw.text((cell_x + 20, cell_y + 90), info_text, fill="black", font=font_large)
            except Exception as e:
                print(f"Error processing image for PDF: {e}")
        pages.append(page)
    if pages:
        pages[0].save(output_filename, "PDF", resolution=900.0, save_all=True, append_images=pages[1:])
        return True
    return False
