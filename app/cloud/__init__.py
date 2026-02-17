from flask import Blueprint

cloud_bp = Blueprint('cloud', __name__, template_folder='../templates/cloud')

from app.cloud import routes  # noqa: E402, F401
