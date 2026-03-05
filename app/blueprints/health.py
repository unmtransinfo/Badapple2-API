"""
Blueprint for the /health endpoint.
Returns the status of the API and its database connections.
"""

import psycopg2
from config import (
    ALLOWED_DB_NAMES,
    DB_NAME2HOST,
    DB_NAME2PASSWORD,
    DB_NAME2PORT,
    DB_NAME2USER,
)
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    db_status = {}
    all_healthy = True

    for db_name in ALLOWED_DB_NAMES:
        try:
            conn = psycopg2.connect(
                host=DB_NAME2HOST[db_name],
                database=db_name,
                user=DB_NAME2USER[db_name],
                password=DB_NAME2PASSWORD[db_name],
                port=DB_NAME2PORT[db_name],
                connect_timeout=3,
            )
            conn.close()
            db_status[db_name] = "ok"
        except Exception as e:
            db_status[db_name] = f"error: {str(e)}"
            all_healthy = False

    status = "healthy" if all_healthy else "unhealthy"
    response = jsonify({"status": status, "databases": db_status})
    response.status_code = 200 if all_healthy else 503
    return response
