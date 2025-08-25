import os
import math
import shutil
import argparse
import requests
from PIL import Image, ImageDraw, ImageFont

from beta.batch_scraper_2.models.AllTestDetails import AllTestDetails

# Assuming your existing modules are in the correct path
from beta.batch_scraper_2.module import ScraperModule
from mainLogic.utils.Endpoint import Endpoint
from mainLogic.utils.glv_var import debugger


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


# --- Helper Function for PDF Creation ---
def create_a4_pdf_from_images(image_info, base_folder, output_filename, images_per_page):
    """
    Creates a multi-page A4 PDF from images, drawing the question number on each.
    Automatically determines best orientation (portrait/landscape) for each page.

    Args:
        image_info (list): A list of dictionaries, each with 'filename' and 'question_number'.
        base_folder (str): The folder where the source images are located.
        output_filename (str): The path for the output PDF file.
        images_per_page (int): The maximum number of images to fit on one A4 page.
    """
    print(f"--- Creating PDF: '{output_filename}' ---")

    if not image_info:
        print(f"No image information provided. Skipping PDF creation.")
        return

    # A4 dimensions in pixels at 600 DPI (doubled from 300 DPI)
    A4_WIDTH_PX, A4_HEIGHT_PX = 4960, 7016
    
    # Get or download Arial font with smaller size for better fit
    font_large = get_or_download_font(font_size=60)  # For question number
    font_small = get_or_download_font(font_size=45)  # For other info

    pages = []
    # Split the image info into chunks for each page
    info_chunks = [
        image_info[i:i + images_per_page]
        for i in range(0, len(image_info), images_per_page)
    ]

    print(f"Found {len(image_info)} images, creating a PDF with {len(info_chunks)} page(s).")

    for chunk_idx, chunk in enumerate(info_chunks):
        # Analyze images in this chunk to determine best orientation
        total_width = 0
        total_height = 0
        valid_images = 0
        
        for info in chunk:
            img_path = os.path.join(base_folder, info['filename'])
            try:
                with Image.open(img_path) as img:
                    total_width += img.width
                    total_height += img.height
                    valid_images += 1
            except:
                pass
        
        # Determine orientation based on average aspect ratio
        if valid_images > 0:
            avg_aspect = (total_width / valid_images) / (total_height / valid_images)
            use_landscape = avg_aspect > 1.2  # Use landscape if images are generally wide
        else:
            use_landscape = False
        
        # Set page dimensions based on orientation
        if use_landscape:
            page_width, page_height = A4_HEIGHT_PX, A4_WIDTH_PX
            print(f"Page {chunk_idx + 1}: Using LANDSCAPE orientation")
        else:
            page_width, page_height = A4_WIDTH_PX, A4_HEIGHT_PX
            print(f"Page {chunk_idx + 1}: Using PORTRAIT orientation")
        
        # Adjusted margins and padding for 600 DPI
        MARGIN_PX = 200  # Margin around the entire page
        PADDING_PX = 80   # Padding between images
        INFO_HEIGHT = 300 # Reserved height for info text above each image
        
        page_canvas = Image.new('RGB', (page_width, page_height), 'white')
        draw_canvas = ImageDraw.Draw(page_canvas)
        num_images_on_page = len(chunk)

        # Calculate optimal grid layout
        cols = int(math.ceil(math.sqrt(num_images_on_page)))
        rows = int(math.ceil(num_images_on_page / cols))
        
        # Adjust grid for landscape orientation
        if use_landscape and cols < rows:
            cols, rows = rows, cols

        # Calculate available space for each cell
        total_padding_x = (cols - 1) * PADDING_PX
        total_padding_y = (rows - 1) * PADDING_PX
        cell_width = (page_width - 2 * MARGIN_PX - total_padding_x) // cols
        cell_height = (page_height - 2 * MARGIN_PX - total_padding_y) // rows

        # Available space for image (excluding info area)
        available_img_height = cell_height - INFO_HEIGHT

        for i, info in enumerate(chunk):
            col = i % cols
            row = i // cols

            img_path = os.path.join(base_folder, info['filename'])
            try:
                img = Image.open(img_path).convert("RGB")
                
                # Calculate scaling to maximize area usage while maintaining aspect ratio
                img_aspect = img.width / img.height
                cell_aspect = cell_width / available_img_height
                
                if img_aspect > cell_aspect:
                    # Image is wider than cell - fit to width
                    new_width = cell_width - 20  # Small margin
                    new_height = int(new_width / img_aspect)
                else:
                    # Image is taller than cell - fit to height
                    new_height = available_img_height - 20  # Small margin
                    new_width = int(new_height * img_aspect)
                
                # Resize image using high-quality resampling
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Calculate cell position
                cell_x = MARGIN_PX + col * (cell_width + PADDING_PX)
                cell_y = MARGIN_PX + row * (cell_height + PADDING_PX)
                
                # Center image within its cell (below info area)
                paste_x = cell_x + (cell_width - img.width) // 2
                paste_y = cell_y + INFO_HEIGHT + (available_img_height - img.height) // 2

                page_canvas.paste(img, (paste_x, paste_y))

                # --- Draw Question Info with better spacing ---
                # Create info box background for better readability
                info_box_coords = [cell_x, cell_y, cell_x + cell_width, cell_y + INFO_HEIGHT - 20]
                draw_canvas.rectangle(info_box_coords, fill="white", outline="lightgray", width=2)
                
                # Get all info except link, question_number, and filename
                excluded_keys = {'link', 'question_number', 'filename'}
                tabular_info = {k: v for k, v in info.items() if k not in excluded_keys}

                # Draw question number prominently
                q_num_text = f"Question {info['question_number']}"
                draw_canvas.text(
                    (cell_x + 20, cell_y + 20), 
                    q_num_text, 
                    fill="black", 
                    font=font_large
                )
                
                # Draw other info in a compact format
                info_y_offset = 90
                line_height = 50
                
                for key, value in tabular_info.items():
                    # Format key name
                    display_key = key.replace('_', ' ').title()
                    info_text = f"{display_key}: {str(value)[:30]}"  # Truncate long values
                    
                    # Check if text fits in the cell width
                    text_bbox = draw_canvas.textbbox((0, 0), info_text, font=font_small)
                    text_width = text_bbox[2] - text_bbox[0]
                    
                    if text_width > cell_width - 40:
                        # Truncate text if too long
                        info_text = info_text[:int(len(info_text) * (cell_width - 40) / text_width)] + "..."
                    
                    draw_canvas.text(
                        (cell_x + 20, cell_y + info_y_offset), 
                        info_text, 
                        fill="darkgray", 
                        font=font_small
                    )
                    info_y_offset += line_height
                    
                    # Stop if we're running out of space
                    if info_y_offset > INFO_HEIGHT - 40:
                        break

                # Draw a subtle border around the image area
                img_border_coords = [
                    cell_x + 10, 
                    cell_y + INFO_HEIGHT - 10, 
                    cell_x + cell_width - 10, 
                    cell_y + cell_height - 10
                ]
                draw_canvas.rectangle(img_border_coords, outline="lightgray", width=1)

            except (IOError, FileNotFoundError) as e:
                print(f"Warning: Could not process image {info['filename']}. Error: {e}")
                # Draw error placeholder
                draw_canvas.rectangle(
                    [cell_x, cell_y, cell_x + cell_width, cell_y + cell_height],
                    outline="red",
                    width=3
                )
                draw_canvas.text(
                    (cell_x + 20, cell_y + cell_height // 2),
                    "Image Load Error",
                    fill="red",
                    font=font_small
                )

        pages.append(page_canvas)

    if pages:
        # Save with higher DPI (600)
        pages[0].save(
            output_filename, 
            "PDF", 
            resolution=600.0,  # Increased from 100.0
            save_all=True, 
            append_images=pages[1:]
        )
        print(f"✅ Successfully created '{output_filename}' with {len(pages)} pages")


def main():
    # --- 1. Add argparse to handle command-line arguments ---
    parser = argparse.ArgumentParser(description="Downloads and creates PDFs for wrong and unattempted questions from a test.")
    parser.add_argument("--test_id", type=str, help="The ID of the test to process.")
    parser.add_argument("--images_per_page", type=int, default=4, help="Number of images per page (default: 4)")
    args = parser.parse_args()

    # --- Configuration ---
    IMAGES_PER_PAGE = args.images_per_page

    WRONG_Q_DIR = "wrong_questions"
    UNATTEMPTED_Q_DIR = "unattempted_questions"

    os.makedirs(WRONG_Q_DIR, exist_ok=True)
    os.makedirs(UNATTEMPTED_Q_DIR, exist_ok=True)

    test_id = args.test_id

    if not test_id:
        all_test = AllTestDetails.from_json(Endpoint(
            url="https://api.penpencil.co/v3/test-service/tests?testType=All&testStatus=All&attemptStatus=All&batchId=678b4cf5a3a368218a2b16e7&isSubjective=false&isPurchased=true&testCategoryIds=6814be5e9467bd0a54703a94",
            headers=ScraperModule.batch_api.DEFAULT_HEADERS
        ).fetch()[0])
        for test in all_test.data:
            print(test.name,"\t",test.testStudentMappingId)
        test_id = input("Enter the test ID: ")

    try:
        # --- 2. Fetch Data using the provided test_id ---
        print("Fetching test data...")
        test = ScraperModule.batch_api.get_test(test_id).data
        questions = test.questions
        print(f"Found {len(questions)} total questions.")

        # --- 3. Prepare Info & Download ---
        wrong_q_info = []
        unattempted_q_info = []

        for i, q in enumerate(questions):
            option = q.yourResult.markedSolutions[0] if q.yourResult.markedSolutions else None
            if option:
                options = [op._id for op in q.question.options]
                index = options.index(option)
                option = q.question.options[index].texts.en if index < len(q.question.options) else None
            info_dict = {
                "link": q.question.imageIds.link,
                "question_number": str(q.question.questionNumber),
                "time_taken": getattr(q.yourResult, 'timeTaken', 'N/A'),
                "subject": str(q.question.topicId.name),
                "marked_solution":str(option if option else 'X'),
                # Prepend question number to filename for sorting
                "filename": f"q{q.question.questionNumber:03d}_{q.question.imageIds.name}-{i}.png"
            }
            if q.yourResult.status == "WRONG":
                wrong_q_info.append(info_dict)
            elif q.yourResult.status == "UnAttempted":
                unattempted_q_info.append(info_dict)

        # Download Wrong questions
        print(f"\nDownloading {len(wrong_q_info)} WRONG questions...")
        for info in wrong_q_info:
            ScraperModule().download_file(
                url=info['link'],
                destination_folder=WRONG_Q_DIR,
                filename=info['filename']
            )

        # Download Unattempted questions
        print(f"\nDownloading {len(unattempted_q_info)} UNATTEMPTED questions...")
        for info in unattempted_q_info:
            ScraperModule().download_file(
                url=info['link'],
                destination_folder=UNATTEMPTED_Q_DIR,
                filename=info['filename']
            )

        print("\nAll downloads complete.")

        # --- 4. Create A4 PDFs ---
        create_a4_pdf_from_images(
            image_info=wrong_q_info,
            base_folder=WRONG_Q_DIR,
            output_filename=f"{test.test.name}_WRONG.pdf",
            images_per_page=IMAGES_PER_PAGE
        )

        create_a4_pdf_from_images(
            image_info=unattempted_q_info,
            base_folder=UNATTEMPTED_Q_DIR,
            output_filename=f"{test.test.name}_UNATTEMPTED.pdf",
            images_per_page=IMAGES_PER_PAGE
        )

    finally:
        # --- 5. Cleanup ---
        print("\n--- Cleaning up temporary files ---")
        for folder in [WRONG_Q_DIR, UNATTEMPTED_Q_DIR]:
            if os.path.exists(folder):
                try:
                    shutil.rmtree(folder)
                    print(f"Removed temporary folder: '{folder}'")
                except OSError as e:
                    print(f"Error removing folder {folder}: {e}")


if __name__ == "__main__":
    main()
