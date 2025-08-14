# `api.py`

This script is the main entry point for the Flask web application. It initializes the Flask app, registers all the blueprints, and starts the development server.

## Flask App Initialization

The script initializes a Flask application and enables Cross-Origin Resource Sharing (CORS).

```python
app = Flask(__name__)
CORS(app)
```

## Managers and Output Directory

It initializes the `Boss`, which in turn initializes the `ClientManager` and `TaskManager`. It also sets the output directory for the downloaded videos.

```python
client_manager = Boss.client_manager
task_manager = Boss.task_manager
OUT_DIR = Boss.OUT_DIR
```

If the output directory does not exist, it is created. If creation fails, it defaults to the current directory.

## Blueprints Registration

The script imports and registers all the necessary blueprints for the application. This includes blueprints for handling preferences, creating tasks, managing sessions, and more.

```python
app.register_blueprint(api_prefs)
app.register_blueprint(legacy_create_task)
app.register_blueprint(template_blueprint)
app.register_blueprint(session_lodge)
app.register_blueprint(dl_and_post_dl)
app.register_blueprint(client_info)
app.register_blueprint(admin)
app.register_blueprint(scraper_blueprint)
app.register_blueprint(login)
```

It also registers any custom blueprints that might be defined.

```python
for blueprint in custom_blueprints:
    blueprint.register_blueprint(app)
```

## Running the Application

The script checks if it is being run directly and, if so, starts the Flask development server.

```python
if __name__ == '__main__':
    app.run(debug=True, port=7680)
```
