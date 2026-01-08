import os
import math
import shutil
import argparse
import sqlite3
import sys

from mainLogic.utils.glv import Global
from mainLogic.utils.image_utils import create_a4_pdf_from_images
from beta.batch_scraper_2.models.AllTestDetails import AllTestDetails
from report_json_export import export_to_json_v3, send_to_report_generator

# Assuming your existing modules are in the correct path
from beta.batch_scraper_2.module import ScraperModule,prefs 
from mainLogic.utils.Endpoint import Endpoint
from mainLogic.utils.glv_var import debugger

# --- Database Configuration ---
REPORT_GENERATOR_DB = prefs.get('db_path','')


def check_if_tag_exists(tag):
    """Checks if a PDF with the given tag exists in the Report-Generator database."""
    if not os.path.exists(REPORT_GENERATOR_DB):
        return False
    try:
        conn = sqlite3.connect(REPORT_GENERATOR_DB)
        cursor = conn.cursor()
        # Check if the tag exists in the tags column
        cursor.execute("SELECT 1 FROM generated_pdfs WHERE tags LIKE ?", (f'%{tag}%',))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    except sqlite3.Error as e:
        print(f"Database error while checking for tag: {e}")
        return False

def _process_question_info(q, i):



    actual_option = None
    actual_option_id  = q.question.solutions[0]
    for _option in q.question.options:
        if _option._id == actual_option_id:
            actual_option = _option.texts.en
#            debugger.var(actual_option)


    marked_option = None
    marked_bool = len(q.yourResult.markedSolutions) > 0
    marked_option_id = q.yourResult.markedSolutions[0] if marked_bool else None

    for _option in q.question.options:
        if _option._id == marked_option_id:
            marked_option = _option.texts.en

    # if actual_option and q.question and q.question.options:
    #     try:
    #         options = [op._id for op in q.question.options]
    #         index = options.index(actual_option)
    #         #actual_option = q.question.options[index].texts.en if index < len(q.question.options) else None
    #     except (ValueError, IndexError) as e :
    #         debugger.error("Error processing actual option")
    #         debugger.var(e)
    #         actual_option = None

    return {
        "link": q.question.imageIds.link if q.question and q.question.imageIds else "",
        "question_number": str(q.question.questionNumber) if q.question else "",
        "time_taken": getattr(q.yourResult, 'timeTaken', 'N/A') if q.yourResult else 'N/A',
        "subject": str(q.question.topicId.name) if q.question and q.question.topicId else "",
        "marked_solution": str(marked_option if marked_option else 'X'),
        "actual_solution": str(actual_option),
        "status": q.yourResult.status if q.yourResult else "",
        "filename": f"q{q.question.questionNumber:03d}_{q.question.imageIds.name}-{i}.png" if q.question and q.question.imageIds else f"q{i:03d}_unknown.png"
    }

def process_test(test_id, test_name, test_mapping_id, args):
    """Processes a single test: download, create PDF, and add to DB."""
    print(f"\n--- Processing Test: {test_name} ({test_id}) ---")

    # Check if report already exists
    if not args.force and check_if_tag_exists(test_mapping_id):
        print(f"Report with tag '{test_mapping_id}' already exists. Skipping.")
        return

    try:
        # --- Fetch Data ---
        print("Fetching test data...")
        test_data = ScraperModule.batch_api.get_test(test_id)
        
        try:
            result_data = Endpoint(
                url=f"https://api.penpencil.co/v3/test-service/tests/{test_id}/my-result?testId={test_id}&testMappingId={test_mapping_id}",
                headers=ScraperModule.batch_api.DEFAULT_HEADERS,
            ).fetch()[0]
            if result_data.get('success') and 'data' in result_data:
                Global.hr()
                print("\n"*3)
                debugger.info("RANK\t"+str(result_data['data'].get('rank', 'N/A')))
                print("\n"*3)
                Global.hr()
        except Exception as re:
            debugger.error(f"Could not fetch rank/result data: {re}")

        if not test_data or not test_data.data:
            print("Could not fetch test data.")
            return

        test = test_data.data
        questions = test.questions
        print(f"Found {len(questions)} total questions.")

        # --- Prepare Info & Download ---
        wrong_q_info = []
        unattempted_q_info = []

        for i, q in enumerate(questions):
            info_dict = _process_question_info(q, i)
            if info_dict['status'] == "WRONG":
                wrong_q_info.append(info_dict)
            elif info_dict['status'] == "UnAttempted":
                unattempted_q_info.append(info_dict)

        WRONG_Q_DIR = "wrong_questions"
        UNATTEMPTED_Q_DIR = "unattempted_questions"
        
        # NEW: JSON Export Logic
        if args.json_export:
            questions_json = []
            for info in wrong_q_info + unattempted_q_info:
                questions_json.append({
                    "question_number": info.get('question_number', ''),
                    "image_url": info.get('link', ''),
                    "status": info.get('status', '').lower(),
                    "marked_solution": info.get('marked_solution', ''),
                    "correct_solution": info.get('actual_solution', ''),
                    "subject": info.get('subject', ''),
                    "time_taken": int(info['time_taken']) if str(info.get('time_taken', '')).isdigit() else 0
                })
            
            json_file = export_to_json_v3(
                test_id, test_name, test_mapping_id,
                questions_json, args
            )
            
            if args.send_to_api:
                send_to_report_generator(json_file, args.api_url)
            
            # Skip PDF generation and local image cleanup if exporting to JSON
            return

        # Original PDF generation logic (only executed if not json_export)
        os.makedirs(WRONG_Q_DIR, exist_ok=True)
        os.makedirs(UNATTEMPTED_Q_DIR, exist_ok=True)

        # Download questions
        for info in wrong_q_info:
            if info['link']: ScraperModule().download_file(info['link'], WRONG_Q_DIR, info['filename'])
        for info in unattempted_q_info:
            if info['link']: ScraperModule().download_file(info['link'], UNATTEMPTED_Q_DIR, info['filename'])
        print("All downloads complete.")

        # --- Create PDFs & Add to DB ---
        subject = args.subject if args.subject else test_name
        # Combine mapping ID with any user-provided tags
        all_tags = f"{test_mapping_id},{args.tags}" if args.tags else test_mapping_id

        if wrong_q_info:
            pdf_filename = f"{test_name}_WRONG.pdf"
            create_a4_pdf_from_images(wrong_q_info, WRONG_Q_DIR, pdf_filename, args.images_per_page, args.orientation, args.grid_rows, args.grid_cols)

        if unattempted_q_info:
            pdf_filename = f"{test_name}_UNATTEMPTED.pdf"
            create_a4_pdf_from_images(unattempted_q_info, UNATTEMPTED_Q_DIR, pdf_filename, args.images_per_page, args.orientation, args.grid_rows, args.grid_cols)

    except Exception as e:
        print(f"An error occurred while processing test {test_id}: {e}")
    finally:
        # Cleanup
        for folder in ["wrong_questions", "unattempted_questions"]:
            if os.path.exists(folder):
                shutil.rmtree(folder)

def main():
    parser = argparse.ArgumentParser(description="Downloads test reports and adds them to the Report-Generator.")
    parser.add_argument("--test_id", type=str, help="The ID of the test to process.")
    parser.add_argument("--images_per_page", type=int, default=4, help="Number of images per page.")
    parser.add_argument("--orientation", type=str, default='portrait', help="Orientation of the PDF pages (portrait or landscape).")
    parser.add_argument("--grid_rows", type=int, help="Number of rows in the grid.")
    parser.add_argument("--grid_cols", type=int, help="Number of columns in the grid.")
    parser.add_argument("--json_export", action='store_true', help='Export as JSON v3.0 instead of generating PDF.')
    parser.add_argument("--send_to_api", action='store_true', help='Send JSON to Report-Generator API.')
    parser.add_argument("--api_url", type=str, default='https://jaimodiji-report-generator.hf.space/json_upload_v3', help='Report-Generator API endpoint.')
    parser.add_argument("--auto_generate", action='store_true', help='Auto-generate PDF on Report-Generator (set view=true in JSON).')
    parser.add_argument("--output_dir", type=str, help='Directory to save the JSON file when using --json_export.')
    parser.add_argument("--final", action='store_true', help="Add the generated PDF(s) to the Report-Generator database.")
    parser.add_argument('--subject', type=str, help='Subject for the PDF. Defaults to the test name.')
    parser.add_argument('--tags', type=str, help='Comma-separated tags for the PDF.')
    parser.add_argument('--notes', type=str, help='Notes for the PDF.')
    parser.add_argument('--all', action='store_true', help='Process all available tests.')
    parser.add_argument('--force', action='store_true', help='Force processing even if report already exists (used with --all).')
    args = parser.parse_args()

    if args.send_to_api:
        args.json_export = True

    new_api_url = "https://api.penpencil.co/v3/test-service/tests?testType=All&testStatus=All&attemptStatus=All&batchId=678b4cf5a3a368218a2b16e7&isSubjective=false&isPurchased=true&testCategoryIds=6814be5e9467bd0a54703a94"
    #new_api_url = "https://api.penpencil.co/v3/test-service/tests?testType=All&testStatus=All&attemptStatus=All&batchId=68d626499dfdb652ac3ea3df&isSubjective=false&categoryId=68d654f20b83f446958276c6&categorySectionId=Other_Tests&isPurchased=true&testCategoryIds=68d654f20b83f446958276c6"

    all_test_data = Endpoint(
        url=new_api_url,
        headers=ScraperModule.batch_api.DEFAULT_HEADERS
    ).fetch()
    debugger.var([[data.get('name',""),data.get('testStudentMappingId',"")] for data in all_test_data[0]['data']])


    if args.all:
        print("--- Processing all available tests ---")
        try:
            all_test_data = Endpoint(
                url=new_api_url,
                headers=ScraperModule.batch_api.DEFAULT_HEADERS
            ).fetch()
            debugger.var(all_test_data[0])
            if all_test_data:
                all_tests = AllTestDetails.from_json(all_test_data[0])
                for test in all_tests.data:
                    process_test(test.testStudentMappingId, test.name, test.testStudentMappingId, args)
            else:
                print("Could not fetch the list of tests.")
        except Exception as e:
            print(f"An error occurred while fetching the list of tests: {e}")
    elif args.test_id:
        # To get the test name and mapping ID, we still need to fetch the list
        try:
            all_test_data = Endpoint(
                url=new_api_url,
                headers=ScraperModule.batch_api.DEFAULT_HEADERS
            ).fetch()
            if all_test_data:
                all_tests = AllTestDetails.from_json(all_test_data[0])
                found_test = next((t for t in all_tests.data if t.testStudentMappingId == args.test_id), None)
                if found_test:
                    process_test(found_test.testStudentMappingId, found_test.name, found_test.testStudentMappingId, args)
                else:
                    print(f"Test with ID '{args.test_id}' not found.")
            else:
                print("Could not fetch the list of tests to find the test name.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("Please provide either --test_id or --all.")

if __name__ == "__main__":
    main()
