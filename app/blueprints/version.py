# blueprints/version.py
# This is the master blueprint directory,
# All new blueprints should be assigned here
from blueprints import scaffold_search
from blueprints.compound_search import compound_search
from blueprints.substance_search import substance_search
from flask import Blueprint


def register_routes(app, in_production: bool, version_url_prefix: str):
    version = Blueprint("version", __name__, url_prefix=version_url_prefix)
    if not (in_production):
        # do not register these blueprints/routes in prod bc
        # 1) we don't include the activity table in the DBs
        # 2) even if we did include the activity table, these API calls are quite computationally expensive
        version.register_blueprint(substance_search)
        scaffold_search.include_dev_only_routes()

    version.register_blueprint(compound_search)
    version.register_blueprint(scaffold_search.scaffold_search)
    app.register_blueprint(version)
