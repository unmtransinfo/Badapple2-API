# blueprints/version.py
# This is the master blueprint directory,
# All new blueprints should be assigned here
from blueprints.compound_search import compound_search
from blueprints.scaffold_search import scaffold_search
from blueprints.substance_search import substance_search
from flask import Blueprint

from app.blueprints.hiers_api import hiers_api

# Set the route prefix based on version
version = Blueprint("version", __name__, url_prefix="/api/v1")

# Register routes
version.register_blueprint(hiers_api)
version.register_blueprint(compound_search)
version.register_blueprint(scaffold_search)
version.register_blueprint(substance_search)
