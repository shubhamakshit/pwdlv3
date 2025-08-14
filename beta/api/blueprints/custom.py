import json
import urllib.parse

import urllib3
#from flask import Blueprint, jsonify, request
from beta.batch_scraper_2.Endpoints import Endpoints
from mainLogic.utils.dependency_checker import re_check_dependencies
from mainLogic.utils.glv import Global
from mainLogic.utils.glv_var import debugger
from mainLogic.utils import glv_var


   
from flask import Blueprint, render_template, jsonify, request, abort
from functools import wraps
import traceback
import logging

class CustomBlueprint:
    def __init__(
            self,
            blueprint_name,
            url_prefix=None,
            template_folder=None,
            static_folder=None,
            static_url_path=None,
            url_defaults=None,
            subdomain=None,
            enable_cors=False
    ):
        """
        Initialize a CustomBlueprint with enhanced features.
        
        Args:
            blueprint_name (str): Name of the blueprint
            url_prefix (str): URL prefix for all routes in this blueprint
            template_folder (str): Template folder path for this blueprint
            static_folder (str): Static files folder path
            static_url_path (str): URL path for static files
            url_defaults (dict): Default values for URL variables
            subdomain (str): Subdomain for this blueprint
            enable_cors (bool): Enable CORS headers for all routes
        """
        self.blueprint = Blueprint(
            blueprint_name, 
            __name__, 
            url_prefix=url_prefix,
            template_folder=template_folder,
            static_folder=static_folder,
            static_url_path=static_url_path,
            url_defaults=url_defaults,
            subdomain=subdomain
        )
        self.blueprint_name = blueprint_name
        self.enable_cors = enable_cors
        self.routes = []
        self.error_handlers = {}
        self.before_request_handlers = []
        self.after_request_handlers = []
        
        # Setup default error handlers
        self._setup_default_error_handlers()
        
        # Setup CORS if enabled
        if self.enable_cors:
            self._setup_cors()

    def add_route(self, url, func, methods=['GET'], endpoint=None, **options):
        """
        Add a route to the blueprint with enhanced error handling.
        
        Args:
            url (str): URL pattern for the route
            func (callable): View function
            methods (list): HTTP methods allowed
            endpoint (str): Endpoint name (defaults to function name)
            **options: Additional options for add_url_rule
        """
        wrapped_func = self._wrap_view_function(func)
        
        route_info = {
            'url': url,
            'func': func,
            'methods': methods,
            'endpoint': endpoint or func.__name__,
            'options': options
        }
        self.routes.append(route_info)
        
        self.blueprint.add_url_rule(
            url, 
            endpoint=endpoint, 
            view_func=wrapped_func, 
            methods=methods,
            **options
        )
        
        return self

    def add_template_route(self, url, template, methods=['GET'], context_func=None, **options):
        """
        Add a route that renders a template.
        
        Args:
            url (str): URL pattern
            template (str): Template filename
            methods (list): HTTP methods
            context_func (callable): Function that returns template context
            **options: Additional options
        """
        def view_func():
            context = context_func() if context_func else {}
            return render_template(template, **context)
        
        view_func.__name__ = f"render_{template.replace('.', '_').replace('/', '_')}"
        return self.add_route(url, view_func, methods, **options)

    def add_json_route(self, url, func, methods=['GET'], **options):
        """
        Add a route that automatically returns JSON responses.
        
        Args:
            url (str): URL pattern
            func (callable): Function that returns data to be JSONified
            methods (list): HTTP methods
            **options: Additional options
        """
        def json_view_func():
            result = func()
            if isinstance(result, tuple):
                data, status_code = result
                return jsonify(data), status_code
            return jsonify(result)
        
        json_view_func.__name__ = f"json_{func.__name__}"
        return self.add_route(url, json_view_func, methods, **options)

    def add_api_route(self, url, func, methods=['GET'], validate_json=False, **options):
        """
        Add an API route with built-in JSON handling and validation.
        
        Args:
            url (str): URL pattern
            func (callable): API function
            methods (list): HTTP methods
            validate_json (bool): Validate JSON input for POST/PUT requests
            **options: Additional options
        """
        def api_view_func():
            try:
                # Handle JSON input validation
                if validate_json and request.method in ['POST', 'PUT', 'PATCH']:
                    if not request.is_json:
                        return jsonify({'error': 'Content-Type must be application/json'}), 400
                    
                    json_data = request.get_json()
                    if json_data is None:
                        return jsonify({'error': 'Invalid JSON'}), 400
                
                # Call the function
                if request.method in ['POST', 'PUT', 'PATCH'] and validate_json:
                    result = func(json_data)
                else:
                    result = func()
                
                # Handle different return types
                if isinstance(result, tuple):
                    if len(result) == 2:
                        data, status_code = result
                        return jsonify(data), status_code
                    elif len(result) == 3:
                        data, status_code, headers = result
                        return jsonify(data), status_code, headers
                
                return jsonify(result)
                
            except ValueError as e:
                return jsonify({'error': 'Validation error', 'message': str(e)}), 400
            except Exception as e:
                logging.error(f"API error in {func.__name__}: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        api_view_func.__name__ = f"api_{func.__name__}"
        return self.add_route(url, api_view_func, methods, **options)

    def error_handler(self, error_code):
        """
        Decorator to add custom error handlers.
        
        Args:
            error_code (int): HTTP error code to handle
        """
        def decorator(func):
            self.error_handlers[error_code] = func
            self.blueprint.errorhandler(error_code)(func)
            return func
        return decorator

    def before_request(self, func):
        """
        Decorator to add before_request handlers.
        """
        self.before_request_handlers.append(func)
        self.blueprint.before_request(func)
        return func

    def after_request(self, func):
        """
        Decorator to add after_request handlers.
        """
        self.after_request_handlers.append(func)
        self.blueprint.after_request(func)
        return func

    def _wrap_view_function(self, func):
        """
        Wrap view functions with error handling and logging.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f"Error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
                
                # Check if it's an API route (returns JSON)
                if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
                    return jsonify({
                        'error': 'Internal server error',
                        'message': str(e) if hasattr(e, 'message') else 'An unexpected error occurred'
                    }), 500
                else:
                    # For regular routes, you might want to render an error template
                    return render_template('error.html', error=str(e)), 500
        
        return wrapper

    def _setup_default_error_handlers(self):
        """
        Setup default error handlers for common HTTP errors.
        """
        @self.blueprint.errorhandler(404)
        def not_found_error(error):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Not found'}), 404
            return render_template('404.html'), 404

        @self.blueprint.errorhandler(500)
        def internal_error(error):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Internal server error'}), 500
            return render_template('500.html'), 500

        @self.blueprint.errorhandler(403)
        def forbidden_error(error):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Forbidden'}), 403
            return render_template('403.html'), 403

    def _setup_cors(self):
        """
        Setup CORS headers for all routes in this blueprint.
        """
        @self.blueprint.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response

    def register_blueprint(self, app):
        """
        Register this blueprint with a Flask app.
        
        Args:
            app: Flask application instance
        """
        app.register_blueprint(self.blueprint)

    def get_routes_info(self):
        """
        Get information about all routes in this blueprint.
        
        Returns:
            list: List of route information dictionaries
        """
        return self.routes

    def __repr__(self):
        return f"<CustomBlueprint '{self.blueprint_name}' with {len(self.routes)} routes>"





# Example usage demonstrating the enhanced features:
# Create a powerful custom blueprint
api_bp = CustomBlueprint(
        "api", 
        url_prefix="/api/v1", 
        enable_cors=True
    )
        
# JSON API route
def get_users():
    return {"users": ["Alice", "Bob", "Charlie"]}

#@app.route('/api/parse-json', methods=['POST'])
def parse_json():
    """
    Endpoint to parse and validate JSON data
    Returns the parsed JSON or error message
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Get the JSON string from the request
        json_string = data.get('json_string', '')
        
        if not json_string:
            return jsonify({
                'success': False,
                'error': 'JSON string is empty'
            }), 400
        
        # Try to parse the JSON
        try:
            parsed_json = json.loads(json_string)
        except json.JSONDecodeError as e:
            return jsonify({
                'success': False,
                'error': f'Invalid JSON: {str(e)}',
                'line': e.lineno if hasattr(e, 'lineno') else None,
                'column': e.colno if hasattr(e, 'colno') else None
            }), 400
        
        # Return the parsed JSON
        return jsonify({
            'success': True,
            'data': parsed_json,
            'stats': {
                'size': len(json_string),
                'type': type(parsed_json).__name__,
                'depth': calculate_depth(parsed_json)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

def calculate_depth(obj, current_depth=0):
    """
    Calculate the maximum depth of a JSON structure
    """
    if isinstance(obj, dict):
        if not obj:
            return current_depth
        return max(calculate_depth(v, current_depth + 1) for v in obj.values())
    elif isinstance(obj, list):
        if not obj:
            return current_depth
        return max(calculate_depth(item, current_depth + 1) for item in obj)
    else:
        return current_depth

#@app.route('/api/format-json', methods=['POST'])
def format_json():
    """
    Endpoint to format/beautify JSON data
    """
    try:
        data = request.get_json()
        json_string = data.get('json_string', '')
        indent = data.get('indent', 2)
        
        try:
            parsed_json = json.loads(json_string)
            formatted_json = json.dumps(parsed_json, indent=indent, sort_keys=False)
            
            return jsonify({
                'success': True,
                'formatted': formatted_json
            }), 200
            
        except json.JSONDecodeError as e:
            return jsonify({
                'success': False,
                'error': f'Invalid JSON: {str(e)}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

#@app.route('/api/minify-json', methods=['POST'])
def minify_json():
    """
    Endpoint to minify JSON data
    """
    try:
        data = request.get_json()
        json_string = data.get('json_string', '')
        
        try:
            parsed_json = json.loads(json_string)
            minified_json = json.dumps(parsed_json, separators=(',', ':'))
            
            return jsonify({
                'success': True,
                'minified': minified_json
            }), 200
            
        except json.JSONDecodeError as e:
            return jsonify({
                'success': False,
                'error': f'Invalid JSON: {str(e)}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


api_bp.add_route("/parse-json", parse_json)

custom_blueprints = [api_bp]


if __name__ == "__main__":
    # Create a powerful custom blueprint
    api_bp = CustomBlueprint(
        "api", 
        url_prefix="/api/v1", 
        enable_cors=True
    )
    
    # Add different types of routes
    
    # Simple route
    @api_bp.add_route("/hello", methods=['GET'])
    def hello():
        return "Hello, World!"
    
    # JSON API route
    def get_users():
        return {"users": ["Alice", "Bob", "Charlie"]}
    
    api_bp.add_json_route("/users", get_users)
    
    # API route with validation
    def create_user(data):
        # Validate required fields
        if 'name' not in data:
            raise ValueError("Name is required")
        
        return {"message": f"User {data['name']} created successfully"}, 201
    
    api_bp.add_api_route("/users", create_user, methods=['POST'], validate_json=True)
    
    # Template route
    def get_dashboard_context():
        return {
            'title': 'Dashboard',
            'user_count': 150,
            'active_sessions': 23
        }
    
    # Create another blueprint for web pages
    web_bp = CustomBlueprint("web", template_folder="templates")
    web_bp.add_template_route("/dashboard", "dashboard.html", context_func=get_dashboard_context)
    
    # Custom error handler
    @api_bp.error_handler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized access'}), 401
    
    # Before request handler
    @api_bp.before_request
    def log_request():
        logging.info(f"API Request: {request.method} {request.path}")
    
    # Usage with Flask app:
    """
    from flask import Flask
    
    app = Flask(__name__)
    api_bp.register_blueprint(app)
    web_bp.register_blueprint(app)
    
    if __name__ == '__main__':
        app.run(debug=True)
    """   
