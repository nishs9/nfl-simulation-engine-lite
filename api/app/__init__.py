from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from api.app.routes import api_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

    # Register blueprints with specific rate limits
    app.register_blueprint(api_bp, url_prefix='/sim-engine-api')

    # Apply rate limits to specific routes
    limiter.limit("100 per minute")(app.view_functions['api_bp.index'])
    limiter.limit("50 per hour")(app.view_functions['api_bp.run_simulation'])
    limiter.limit("20 per hour")(app.view_functions['api_bp.run_simulation_legacy'])

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400

    # Rate limit exceeded handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429

    return app
