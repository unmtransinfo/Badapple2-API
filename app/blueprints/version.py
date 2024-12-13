# blueprints/version.py
# This is the master blueprint directory,
# All new blueprints should be assigned here
from blueprints.compound_search import compound_search
from blueprints.hiers_api import hiers_api
from blueprints.scaffold_search import scaffold_search
from blueprints.substance_search import substance_search
from flask import Blueprint


def register_routes(app, in_production: bool, version_str: str = "1"):
    # Set the route prefix based on version
    version = Blueprint("version", __name__, url_prefix=f"/api/v{version_str}")
    version.register_blueprint(hiers_api)
    version.register_blueprint(compound_search)
    version.register_blueprint(scaffold_search)
    if in_production:
        # do not register substance blueprint in prod bc
        # 1) we don't include the activity table in the DBs
        # 2) even if we did include the activity table, these API calls are quite computationally expensive
        version.register_blueprint(substance_search)
    app.register_blueprint(version)
