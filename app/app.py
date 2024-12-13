from blueprints.version import register_routes
from dotenv import load_dotenv
from flasgger import LazyJSONEncoder, Swagger
from flask import Flask, redirect
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.json_encoder = LazyJSONEncoder
    # Load config
    load_dotenv(".env")
    app.config.from_pyfile("config.py")
    version_str = app.config.get("VERSION", "1")

    # Enhanced CORS configuration
    CORS(app, resources={r"/*": {"origins": "*"}})

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/apidocs/apispec_1.json",
            }
        ],
        "static_url_path": "/badapple2/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "info": {
            "title": "API for Badapple databases",
            "description": "API which allows for programmatic access to badapple_classic and badapple2 DBs.",
            "version": version_str,
        },
    }
    template = {}
    # TODO: set prefix in config
    if app.config.get("FLASK_ENV", "production") == "production":
        template = dict(swaggerUiPrefix="/badapple2")

    swagger = Swagger(app, config=swagger_config, template=template)
    register_routes(app, version_str)
    return app


app = create_app()

if __name__ == "__main__":
    print(app.url_map)
    app.run(host="0.0.0.0", port=app.config.get("APP_PORT"), debug=True)
