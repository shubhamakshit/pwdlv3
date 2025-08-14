# `scraper.py`

This script defines the routes for scraping data from the PW platform. It includes routes for fetching batch details, subjects, chapters, lectures, notes, and DPP PDFs. It also includes routes for the "Khazana" feature.

## Blueprint

The script creates a Flask Blueprint named `scraper`.

```python
scraper_blueprint = Blueprint('scraper', __name__)
```

## Batch API Initialization

The script initializes a `Endpoints` object from `beta.batch_scraper_2.Endpoints` to interact with the PW API. It tries to get the token from the preferences file, and if it fails, it re-checks the dependencies to get the token.

## Helper Functions

### `create_response(data=None, error=None)`

*   **Description:** A helper function to create a JSON response with a consistent format.

### `renamer(data, old_key, new_key)`

*   **Description:** A helper function to rename a key in a list of dictionaries.

## Khazana Routes

These routes are for the "Khazana" feature, which seems to be a separate section of content on the PW platform.

*   `/api/khazana/lecture/<program_name>/<topic_name>/<lecture_id>/<path:lecture_url>`
*   `/api/khazana/<program_name>`
*   `/api/khazana/<program_name>/<subject_name>`
*   `/api/khazana/<program_name>/<subject_name>/<teacher_name>`
*   `/api/khazana/<program_name>/<subject_name>/<teacher_name>/<topic_name>`
*   `/api/khazana/<program_name>/<subject_name>/<teacher_name>/<topic_name>/<sub_topic_name>`

## Batch Routes

These routes are for fetching data from regular batches.

*   `/api/batches/<batch_name>`
*   `/api/batches/<batch_name>/<subject_name>`
*   `/api/batches/<batch_name>/<subject_name>/<chapter_name>/lectures` or `/api/batches/<batch_name>/<subject_name>/<chapter_name>`
*   `/api/batches/<batch_name>/<subject_name>/<chapter_name>/notes`
*   `/api/batches/<batch_name>/<subject_name>/<chapter_name>/dpp_pdf`

## Lecture Info Route

*   `/api/lecture/<batch_name>/<id>`: Fetches the license key and other information for a lecture.

## "Normal" Routes [DEPRECATED]

These routes seem to be for a simplified or alternative way of fetching data.

*   `/normal/subjects` or `/api/normal/subjects`
*   `/normal/chapters/<subject_slug>` or `/api/normal/chapters/<subject_slug>`
*   `/normal/lectures` or `/api/normal/lectures` or `/api/normal/videos`

## Other Routes

*   `/api/batches`: Fetches a list of all batches.
*   `/api/set-token`: Sets the authentication token for the `batch_api` object.
