from flask import Flask
from flask_cors import CORS
from app.routes import api_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(api_bp, url_prefix='/sim-engine-api')

    return app
