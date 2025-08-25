import os
import math
import shutil
import argparse
from PIL import Image, ImageDraw, ImageFont

# Assuming your existing modules are in the correct path
from beta.batch_scraper_2.module import ScraperModule
from mainLogic.utils.glv_var import debugger


# --- Helper Function for PDF Creation ---

def create_a4_pdf_from_images(image_info, base_folder, output_filename, images_per_page):
    """
    Creates a multi-page A4 PDF from images, drawing the question number on each.

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

    # A4 dimensions in pixels at 300 DPI
    A4_WIDTH_PX, A4_HEIGHT_PX = 2480, 3508
    # --- Increased Padding and Margins ---
    MARGIN_PX = 150  # Margin around the entire page
    PADDING_PX = 50  # Padding between images

    # Try to load a standard font, with a fallback
    try:
        font = ImageFont.truetype("arial.ttf", size=30)  # Smaller font for table
    except IOError:
        print("Arial font not found. Using default font.")
        font = ImageFont.load_default()

    pages = []
    # Split the image info into chunks for each page
    info_chunks = [
        image_info[i:i + images_per_page]
        for i in range(0, len(image_info), images_per_page)
    ]

    print(f"Found {len(image_info)} images, creating a PDF with {len(info_chunks)} page(s).")

    for chunk in info_chunks:
        page_canvas = Image.new('RGB', (A4_WIDTH_PX, A4_HEIGHT_PX), 'white')
        draw_canvas = ImageDraw.Draw(page_canvas)
        num_images_on_page = len(chunk)

        cols = int(math.ceil(math.sqrt(num_images_on_page)))
        rows = int(math.ceil(num_images_on_page / cols))

        # Calculate cell size considering the new padding
        total_padding_x = (cols - 1) * PADDING_PX
        total_padding_y = (rows - 1) * PADDING_PX
        cell_width = (A4_WIDTH_PX - 2 * MARGIN_PX - total_padding_x) // cols
        cell_height = (A4_HEIGHT_PX - 2 * MARGIN_PX - total_padding_y) // rows

        for i, info in enumerate(chunk):
            col = i % cols
            row = i // rows

            img_path = os.path.join(base_folder, info['filename'])
            try:
                img = Image.open(img_path).convert("RGB")  # Convert to RGB for consistency

                img.thumbnail((cell_width, cell_height))

                # Calculate position including padding
                paste_x = MARGIN_PX + col * (cell_width + PADDING_PX) + (cell_width - img.width) // 2
                paste_y = MARGIN_PX + row * (cell_height + PADDING_PX) + (cell_height - img.height) // 2

                page_canvas.paste(img, (paste_x, paste_y))

                # --- Draw Question Info Table on Canvas (Dynamic) ---
                # Get all info except link, question_number, and filename
                excluded_keys = {'link', 'question_number', 'filename'}
                tabular_info = {k: v for k, v in info.items() if k not in excluded_keys}

                info_lines = [f"Q: {info['question_number']}"]  # Start with question number

                # Add all other info dynamically
                for key, value in tabular_info.items():
                    # Format key name (capitalize and truncate for display)
                    display_key = key.replace('_', ' ').title()[:8]
                    info_lines.append(f"{display_key}: {value}")

                # Draw each line of info above the image
                for line_idx, line in enumerate(info_lines):
                    text_y = paste_y - 50 - (line_idx * 25)  # Stack lines vertically
                    draw_canvas.text((paste_x, text_y), line, fill="black", font=font)

            except (IOError, FileNotFoundError):
                print(f"Warning: Could not process image {info['filename']}. Skipping.")

        pages.append(page_canvas)

    if pages:
        pages[0].save(
            output_filename, "PDF", resolution=100.0, save_all=True, append_images=pages[1:]
        )
        print(f"✅ Successfully created '{output_filename}'")


def main():
    # --- 1. Add argparse to handle command-line arguments ---
    parser = argparse.ArgumentParser(description="Downloads and creates PDFs for wrong and unattempted questions from a test.")
    parser.add_argument("test_id", type=str, help="The ID of the test to process.")
    args = parser.parse_args()

    # --- Configuration ---
    IMAGES_PER_PAGE = 9

    WRONG_Q_DIR = "wrong_questions"
    UNATTEMPTED_Q_DIR = "unattempted_questions"

    os.makedirs(WRONG_Q_DIR, exist_ok=True)
    os.makedirs(UNATTEMPTED_Q_DIR, exist_ok=True)

    try:
        # --- 2. Fetch Data using the provided test_id ---
        print("Fetching test data...")
        test = ScraperModule.batch_api.get_test(args.test_id).data
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