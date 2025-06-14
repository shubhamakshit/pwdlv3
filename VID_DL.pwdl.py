from beta.batch_scraper_2.module import ScraperModule

batch_name = "yakeen-neet-2-0-2026-854543"

prefs = ScraperModule.prefs
batch_api = ScraperModule.batch_api
debugger = ScraperModule.debugger

subjects = batch_api.get_batch_details(batch_name=batch_name)

for subject in subjects:
    debugger.var(subject.slug)
    