import argparse
from beta.batch_scraper_2.module import ScraperModule
from datetime import datetime, timezone, timedelta
import pytz # Make sure to pip install pytz if you haven't already
from operator import attrgetter # For easier sorting

# Assuming mainLogic.downloader.py contains a function named 'main'
from mainLogic.downloader import main as downloader # Renamed to avoid confusion with internal 'main'

batch_name_default = "yakeen-neet-2-0-2026-854543"

# --- 1. Set up argparse ---
parser = argparse.ArgumentParser(description="Scrape and download lectures from PenPencil batches.")
parser.add_argument(
    "--batch", "-b",
    type=str,
    default=batch_name_default,
    help=f"Name/slug of the batch to scrape (default: {batch_name_default})."
)
parser.add_argument(
    "--subjects", "-s",
    type=str,
    help="Comma-separated list of subject slugs to filter. If not provided, all subjects are processed.",
)
parser.add_argument(
    "--latest-nth", "-n",
    type=int,
    default=None, # No default, means get all latest for each subject by default
    help="Fetch the Nth latest lecture for each subject (0 for the absolute latest, 1 for the second latest, etc.). "
         "If not provided, all lectures (matching --date if set) are considered.",
)
parser.add_argument(
    "--date", "-dt",
    type=str,
    default=None,
    help="Filter lectures to a specific date in 'dd.mm.yyyy' format. "
         "If used with -n, it finds the Nth latest lecture *on that specific date*.",
)
parser.add_argument(
    "--download", "-d",
    action="store_true",
    help="Enable downloading of the selected lecture(s)."
)
parser.add_argument(
    "--download-dir", "-dd",
    type=str,
    default="./" if not ScraperModule.prefs.get("extension_download_dir") else ScraperModule.prefs.get("extension_download_dir"),
    help="Base directory for downloads (default: ./)."
)

args = parser.parse_args()

# --- Apply arguments ---
batch_name = args.batch
# Process subjects_of_interest from command line
if args.subjects:
    subjects_of_interest = set([s.strip() for s in args.subjects.split(',') if s.strip()])
else:
    # If not provided via CLI, fall back to prefs or keep empty for no filtering
    subjects_of_interest = set(ScraperModule.prefs.get("subjects_of_interest", []))

download_enabled = args.download
base_download_directory = args.download_dir

# Parse the specific date filter if provided
specific_date_filter_utc = None
if args.date:
    try:
        # Assuming input is dd.mm.yyyy, convert to datetime object at midnight in IST, then to UTC
        day, month, year = map(int, args.date.split('.'))
        target_date_ist = datetime(year, month, day, 0, 0, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
        specific_date_filter_utc = target_date_ist.astimezone(timezone.utc)
        debugger.info(f"Filtering for lectures on specific date: {args.date} (UTC: {specific_date_filter_utc.date()})")
    except ValueError as e:
        debugger.error(f"Invalid date format for --date: {args.date}. Please use 'dd.mm.yyyy'. Error: {e}")
        exit() # Exit if the date format is incorrect


prefs = ScraperModule.prefs # Still keep prefs for other potential settings
batch_api = ScraperModule.batch_api
debugger = ScraperModule.debugger

# Ensure batch_api is initialized before use
if batch_api is None:
    debugger.error("ScraperModule.batch_api is not initialized. Please check token setup.")
    exit()

all_subjects = batch_api.get_batch_details(batch_name=batch_name)

# Define UTC timezone for consistency
UTC = timezone.utc # Python 3.2+ recommended way for UTC

# Iterate through subjects
for subject in all_subjects:
    # Filter subjects based on preferences (from CLI or prefs file)
    if subjects_of_interest and subject.slug not in subjects_of_interest:
        debugger.info(f"Skipping subject '{subject.slug}' as it's not in subjects of interest.")
        continue

    debugger.var(f"Processing subject: {subject.slug}")
    chapters_in_subject = batch_api.get_batch_subjects(batch_name=batch_name, subject_name=subject.slug)

    all_lectures_in_subject = []
    
    # Iterate through all chapters to collect all relevant lectures
    for chapter in chapters_in_subject:
        if chapter.name and chapter.videos > 0:
            lectures_in_chapter = batch_api.get_batch_chapters(
                batch_name=batch_name,
                subject_name=subject.slug,
                chapter_name=chapter.name
            )
            # Add chapter_name to each lecture object for downloader context
            for lecture in lectures_in_chapter:
                lecture.chapter_name = chapter.name # Dynamically add chapter_name attribute
                all_lectures_in_subject.append(lecture)

    # --- Sort and Filter Lectures ---
    filtered_lectures = []

    if specific_date_filter_utc:
        # Filter by specific date first
        target_date_utc_end = specific_date_filter_utc + timedelta(days=1) # Midnight of next day
        for lecture in all_lectures_in_subject:
            if lecture.startTime and \
               specific_date_filter_utc <= lecture.startTime < target_date_utc_end:
                filtered_lectures.append(lecture)
        if not filtered_lectures:
            debugger.warning(f"No lectures found for subject '{subject.slug}' on date {args.date}.")
            continue # Skip to next subject if no lectures found on specified date
    else:
        # If no specific date, consider all collected lectures
        filtered_lectures = all_lectures_in_subject

    # Sort the filtered lectures by start time in descending order (latest first)
    # Using attrgetter is efficient for sorting by an attribute
    sorted_lectures = sorted(filtered_lectures, key=attrgetter('startTime'), reverse=True)

    selected_lecture = None
    if args.latest_nth is not None:
        if 0 <= args.latest_nth < len(sorted_lectures):
            selected_lecture = sorted_lectures[args.latest_nth]
            debugger.info(f"Selected {args.latest_nth}th latest lecture for subject '{subject.slug}'.")
        else:
            debugger.warning(f"Requested {args.latest_nth}th latest lecture, but only {len(sorted_lectures)} lectures found for subject '{subject.slug}' after date filter (if any).")
            continue # Skip to next subject if nth latest doesn't exist
    elif sorted_lectures: # If no -n is provided, and there are lectures, just pick the very latest
        selected_lecture = sorted_lectures[0]
        debugger.info(f"No --latest-nth specified. Picking the very latest lecture for subject '{subject.slug}'.")

    if selected_lecture:
        debugger.info(f"Processing selected lecture for subject '{subject.slug}':")
        # Ensure tags exist before accessing tags[0].name
        lecture_name = selected_lecture.name if selected_lecture.name else f"Lecture ID: {selected_lecture.id}"
        if selected_lecture.tags:
             lecture_name = selected_lecture.tags[0].name
        
        # Get actual video details to ensure we have the correct ID for downloading
        
        debugger.info(f"  Name: {lecture_name}")
        debugger.info(f"  Start Time: {selected_lecture.startTime.strftime('%d-%m-%Y %H:%M:%S %Z')}")
        debugger.info(f"  Batch Name: {batch_name}")
        debugger.info(f"  Lecture ID: {selected_lecture.id}")
        
        # --- Download Logic ---
        # Pass the chapter name and subject slug to the downloader for structured folders
        if download_enabled:
            debugger.info(f"  Attempting to download lecture...")
            downloader(
                name=lecture_name,
                batch_name=batch_name,
                id=selected_lecture.id,
                directory=base_download_directory,
            )
        
    else:
        debugger.warning(f"No lectures found for subject: {subject.slug} that match the applied filters.")