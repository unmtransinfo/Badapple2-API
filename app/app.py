import yaml
from blueprints.version import register_routes
from config import DEV_ONLY_PATHS
from dotenv import load_dotenv
from flasgger import LazyJSONEncoder, Swagger
from flask import Flask
from flask_cors import CORS


def _load_api_spec() -> dict:
    with open("api_spec.yml", "r") as file:
        api_spec = yaml.safe_load(file)
    return api_spec


def _get_updated_paths(paths_dict: dict, version_url_prefix: str, in_production: bool):
    updated_paths = {}
    for path in paths_dict:
        if not (in_production) or path not in DEV_ONLY_PATHS:
            new_path = version_url_prefix + path
            updated_paths[new_path] = paths_dict[path]
    return updated_paths


def create_app():
    app = Flask(__name__)
    app.json_encoder = LazyJSONEncoder

    # load config
    load_dotenv(".env")
    app.config.from_pyfile("config.py")
    CORS(app, resources={r"/*": {"origins": "*"}})

    # load swagger template
    swagger_template = _load_api_spec()
    VERSION = swagger_template["info"]["version"]
    VERSION_URL_PREFIX = f"/api/v{VERSION}"

    # setup swagger config
    URL_PREFIX = app.config.get("URL_PREFIX", "")
    IN_PROD = app.config.get("FLASK_ENV", "") == "production"
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/apidocs/apispec_1.json",
            }
        ],
        "static_url_path": f"/{URL_PREFIX}/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "ui_params": {
            "url_prefix": (f"/{URL_PREFIX}") if IN_PROD else "",
        },
    }

    # update template to include URL prefixes
    swagger_template.update({"swaggerUiPrefix": f"/{URL_PREFIX}" if IN_PROD else ""})
    swagger_template["paths"] = _get_updated_paths(
        swagger_template["paths"], VERSION_URL_PREFIX, IN_PROD
    )

    # setup swagger and register routes
    swagger = Swagger(app, config=swagger_config, template=swagger_template)
    register_routes(app, IN_PROD, VERSION_URL_PREFIX)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=app.config.get("APP_PORT"), debug=True)
