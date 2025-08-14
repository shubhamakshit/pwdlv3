# `template_routes.py`

This script defines the routes for serving the main HTML templates of the web application.

## Blueprint

The script creates a Flask Blueprint named `template_blueprint`.

```python
template_blueprint = Blueprint('template_blueprint', __name__)
```

## Routes

All of the routes in this script simply render the `index.html` template. This is likely because the frontend is a single-page application (SPA) that handles its own routing.

*   `/`: The root URL.
*   `/util`: The utilities page.
*   `/prefs`: The preferences page.
*   `/help`: The help page.
*   `/sessions`: The sessions page.
*   `/admin`: The admin page.
*   `/boss`: The boss page.
*   `/login`: The login page.
*   `/profile`: The profile page.
