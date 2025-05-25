from flask import Flask, jsonify
from flask_cors import CORS
from app.routes import api_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(api_bp, url_prefix='/sim-engine-api')

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400

    return app
