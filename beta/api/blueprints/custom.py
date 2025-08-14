from flask import Blueprint, render_template, jsonify, request, abort
from functools import wraps
import traceback
from mainLogic.utils.glv_var import debugger
from beta.batch_scraper_2.module import ScraperModule

# --- Serialization Helper ---
def serialize(obj):
    """
    Recursively serialize model objects to a dictionary, handling nested objects and datetimes.
    """
    if hasattr(obj, 'isoformat'):  # Handle datetime objects
        return obj.isoformat()
    if hasattr(obj, '__dict__'):
        return {k: serialize(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    elif isinstance(obj, list):
        return [serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    else:
        return obj

# --- Custom Blueprint Class ---
class CustomBlueprint:
    def __init__(
            self,
            blueprint_name,
            url_prefix=None,
            enable_cors=False,
            **kwargs
    ):
        """
        Initialize a CustomBlueprint with enhanced features.
        """
        self.blueprint = Blueprint(blueprint_name, __name__, url_prefix=url_prefix, **kwargs)
        self.blueprint_name = blueprint_name
        self.enable_cors = enable_cors
        
        self._setup_default_error_handlers()
        if self.enable_cors:
            self._setup_cors()

    def add_route(self, url, func, **options):
        """
        Add a route to the blueprint with enhanced error handling.
        """
        endpoint = options.get('endpoint', func.__name__)
        wrapped_func = self._wrap_view_function(func)
        self.blueprint.add_url_rule(url, endpoint=endpoint, view_func=wrapped_func, **options)
        return self

    def add_json_route(self, url, func, **options):
        """
        Add a route that automatically returns JSON responses.
        """
        def json_view_func(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, tuple):
                data, status_code = result
                return jsonify(data), status_code
            return jsonify(result)
        
        json_view_func.__name__ = f"json_{func.__name__}"
        return self.add_route(url, json_view_func, **options)

    def _wrap_view_function(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                debugger.error(f"Error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
                return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
        return wrapper

    def _setup_default_error_handlers(self):
        @self.blueprint.errorhandler(404)
        def not_found_error(error):
            return jsonify({'error': 'Not found'}), 404

        @self.blueprint.errorhandler(500)
        def internal_error(error):
            return jsonify({'error': 'Internal server error'}), 500

        @self.blueprint.errorhandler(403)
        def forbidden_error(error):
            return jsonify({'error': 'Forbidden'}), 403

    def _setup_cors(self):
        @self.blueprint.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response

    def register_blueprint(self, app):
        app.register_blueprint(self.blueprint)

# --- Test API Blueprint ---
test_api_bp = CustomBlueprint(
    "test_api", 
    url_prefix="/api/v1/test", 
    enable_cors=True
)

def test_batch_api():
    """
    Endpoint to test the ScraperModule by fetching batch details.
    Requires 'batch_name' as a query parameter.
    """
    batch_name = request.args.get('batch_name')
    if not batch_name:
        return {'error': 'Missing required query parameter: batch_name'}, 400

    try:
        scraper = ScraperModule()
        if not scraper.batch_api:
            debugger.error("Scraper is not properly initialized. Check tokens.")
            return {'error': 'Scraper is not properly initialized.'}, 500

        debugger.info(f"Fetching details for batch: {batch_name}")
        subjects = scraper.batch_api.get_batch_details(batch_name=batch_name)
        
        return serialize(subjects)

    except Exception as e:
        debugger.error(f"Error in test_batch_api: {str(e)} {traceback.format_exc()}")
        return {'error': 'Failed to fetch batch details.', 'message': str(e)}, 500

test_api_bp.add_json_route("/batch-details", test_batch_api, methods=['GET'])

# --- Export Blueprints ---
custom_blueprints = [test_api_bp]
