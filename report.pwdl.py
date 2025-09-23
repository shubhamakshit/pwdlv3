import os
import math
import shutil
import argparse
import requests
from PIL import Image, ImageDraw, ImageFont
from mainLogic.utils.image_utils import get_or_download_font, create_a4_pdf_from_images
from beta.batch_scraper_2.models.AllTestDetails import AllTestDetails

# Assuming your existing modules are in the correct path
from beta.batch_scraper_2.module import ScraperModule
from mainLogic.utils.Endpoint import Endpoint
from mainLogic.utils.glv_var import debugger


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
        try:
            all_test_data = Endpoint(
                url="https://api.penpencil.co/v3/test-service/tests?testType=All&testStatus=All&attemptStatus=All&batchId=678b4cf5a3a368218a2b16e7&isSubjective=false&isPurchased=true&testCategoryIds=6814be5e9467bd0a54703a94",
                headers=ScraperModule.batch_api.DEFAULT_HEADERS
            ).fetch()
            if all_test_data:
                all_test = AllTestDetails.from_json(all_test_data[0])
                for test in all_test.data:
                    print(test.name, "\t", test.testStudentMappingId)
                test_id = input("Enter the test ID: ")
            else:
                print("Could not fetch the list of tests.")
                return
        except Exception as e:
            print(f"An error occurred while fetching the list of tests: {e}")
            return

    try:
        # --- 2. Fetch Data using the provided test_id ---
        print("Fetching test data...")
        test_data = ScraperModule.batch_api.get_test(test_id)
        if not test_data or not test_data.data:
            print("Could not fetch test data.")
            return

        test = test_data.data
        questions = test.questions
        print(f"Found {len(questions)} total questions.")

        # --- 3. Prepare Info & Download ---
        wrong_q_info = []
        unattempted_q_info = []

        for i, q in enumerate(questions):
            option = None
            if q.yourResult and q.yourResult.markedSolutions:
                option = q.yourResult.markedSolutions[0]

            actual_option = None
            if q.topperResult and q.topperResult.markedSolutions:
                actual_option = q.topperResult.markedSolutions[0]

            if option and q.question and q.question.options:
                try:
                    options = [op._id for op in q.question.options]
                    index = options.index(option)
                    option = q.question.options[index].texts.en if index < len(q.question.options) else None
                except (ValueError, IndexError):
                    option = None
            if actual_option and q.question and q.question.options:
                try:
                    options = [op._id for op in q.question.options]
                    index = options.index(actual_option)
                    actual_option = q.question.options[index].texts.en if index < len(q.question.options) else None
                except (ValueError, IndexError):
                    actual_option = None

            info_dict = {
                "link": q.question.imageIds.link if q.question and q.question.imageIds else "",
                "question_number": str(q.question.questionNumber) if q.question else "",
                "time_taken": getattr(q.yourResult, 'timeTaken', 'N/A') if q.yourResult else 'N/A',
                "subject": str(q.question.topicId.name) if q.question and q.question.topicId else "",
                "marked_solution":str(option if option else 'X'),
                "actual_solution":str(actual_option if actual_option else 'X'),
                "filename": f"q{q.question.questionNumber:03d}_{q.question.imageIds.name}-{i}.png" if q.question and q.question.imageIds else f"q{i:03d}_unknown.png"
            }
            if q.yourResult and q.yourResult.status == "WRONG":
                wrong_q_info.append(info_dict)
            elif q.yourResult and q.yourResult.status == "UnAttempted":
                unattempted_q_info.append(info_dict)

        # Download Wrong questions
        print(f"\nDownloading {len(wrong_q_info)} WRONG questions...")
        for info in wrong_q_info:
            if info['link']:
                ScraperModule().download_file(
                    url=info['link'],
                    destination_folder=WRONG_Q_DIR,
                    filename=info['filename']
                )

        # Download Unattempted questions
        print(f"\nDownloading {len(unattempted_q_info)} UNATTEMPTED questions...")
        for info in unattempted_q_info:
            if info['link']:
                ScraperModule().download_file(
                    url=info['link'],
                    destination_folder=UNATTEMPTED_Q_DIR,
                    filename=info['filename']
                )

        print("\nAll downloads complete.")

        # --- 4. Create A4 PDFs ---
        if wrong_q_info:
            create_a4_pdf_from_images(
                image_info=wrong_q_info,
                base_folder=WRONG_Q_DIR,
                output_filename=f"{test.test.name if test and test.test else 'Test'}_WRONG.pdf",
                images_per_page=IMAGES_PER_PAGE
            )

        if unattempted_q_info:
            create_a4_pdf_from_images(
                image_info=unattempted_q_info,
                base_folder=UNATTEMPTED_Q_DIR,
                output_filename=f"{test.test.name if test and test.test else 'Test'}_UNATTEMPTED.pdf",
                images_per_page=IMAGES_PER_PAGE
            )

    except Exception as e:
        print(f"An error occurred: {e}")
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