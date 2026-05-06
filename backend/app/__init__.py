from flask import Flask, redirect
from flask_migrate import Migrate
from config import Config
from app.extensions import db
from flask_cors import CORS
from flasgger import Swagger
from dotenv import load_dotenv
import os

migrate = Migrate()
swagger = Swagger()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    load_dotenv()
    
    print("db", os.environ.get("DB_TYPE"))
    
    CORS(app)
    
    app.config['SWAGGER'] = {
        'title': 'NYC Taxi API',
        'description': 'REST API for NYC Taxi Trip Data Analysis',
        'version': '1.0.0',
        'uiversion': 3,
        'specs_route': '/apidocs/',
        'specs': [
            {
                'endpoint': 'apispec',
                'route': '/apispec.json',
                'rule_filter': lambda rule: True,
                'model_filter': lambda tag: True,
            }
        ],
        'static_url_path': '/flasgger_static',
    }

    db.init_app(app)
    migrate.init_app(app, db)
    swagger.init_app(app)

    from app.models import Zone, Trip

    from app.routes.trips import trips_bp
    from app.routes.zones import zones_bp
    from app.routes.analytics import analytics_bp
    app.register_blueprint(trips_bp)
    app.register_blueprint(zones_bp)
    app.register_blueprint(analytics_bp)

    @app.route('/')
    def index():
        return redirect('/apidocs/')

    return app