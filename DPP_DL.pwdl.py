import argparse
from datetime import date, timedelta # Import timedelta for date manipulation

from beta.batch_scraper_2.module import ScraperModule
from mainLogic.utils.glv_var import debugger

batch_name = "yakeen-neet-2-0-2026-854543"

def main():
    parser = argparse.ArgumentParser(description="Download educational content based on date filters.")
    parser.add_argument("--all", action="store_true", help="Download all content irrespective of dates.")
    parser.add_argument("--current-date-ge", action="store_true", help="Download content with dates greater than or equal to the current date.")
    parser.add_argument("--one-day-less", action="store_true", help="Download content with dates one day less than the current date.")
    parser.add_argument("--latest", action="store_true", help="Download only the latest content available.")

    args = parser.parse_args()

    yakeen = ScraperModule.batch_api.get_batch_details(
        batch_name=batch_name
    )

    for subject in yakeen:
        slug = subject.slug
        subject_details = ScraperModule.batch_api.get_batch_subjects(
            batch_name=batch_name,
            subject_name=slug
        )
        debugger.warning(f"Subject Name: {subject.slug}")
        for chapter in subject_details:
            chapter_name = chapter.name
            if chapter.videos > 0 and chapter.exercises > 0:
                debugger.info(f"Chapter Name: {chapter_name}")
                dpp_notes = ScraperModule.batch_api.get_batch_dpp_notes(
                    batch_name=batch_name,
                    subject_name=slug,
                    chapter_name=chapter_name
                )

                # Sort DPPs by date in descending order for --latest functionality
                if args.latest:
                    dpp_notes.sort(key=lambda d: d.date if d.date else date.min, reverse=True)

                for i, dpp in enumerate(dpp_notes):
                    # Ensure dpp.date is not None before trying to access its .date() attribute
                    if dpp.date:
                        dpp_date = dpp.date.date()
                        today = date.today()

                        download_this_dpp = False

                        if args.all:
                            download_this_dpp = True
                        elif args.current_date_ge:
                            if dpp_date >= today:
                                download_this_dpp = True
                        elif args.one_day_less:
                            if dpp_date == today - timedelta(days=1):
                                download_this_dpp = True
                        elif args.latest:
                            # Only download the very first (latest) DPP if --latest is active
                            if i == 0:
                                download_this_dpp = True
                        else:
                            # Default behavior if no specific argument is provided (e.g., current_date_ge)
                            if dpp_date >= today:
                                download_this_dpp = True


                        if download_this_dpp:
                            # Add a check to ensure homeworks and attachments exist before accessing
                            if dpp.homeworks and dpp.homeworks[0].attachments:
                                name = dpp.homeworks[0].attachments[0].name
                                link = dpp.homeworks[0].attachments[0].link
                                debugger.info(f"Dpp Notes: {name}")
                                ScraperModule().download_file(
                                    filename=name,
                                    url=link
                                )
                                if args.latest: # Stop after downloading the latest
                                    break
                            else:
                                debugger.warning(f"DPP {dpp.id} has no homeworks or attachments.")
                    else:
                        debugger.warning(f"DPP {dpp.id} has no date specified.")
                if args.latest and dpp_notes: # If --latest was used, we only needed one from this chapter
                    break # Move to the next subject after finding the latest for the current chapter

if __name__ == "__main__":
    main()