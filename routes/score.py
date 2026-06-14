from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from services.score_engine import calculate_credit_score

score_bp = Blueprint("score", __name__)


@score_bp.route("", methods=["GET"])
@jwt_required()
def get_score():
    farmer_id = int(get_jwt_identity())
    result = calculate_credit_score(farmer_id)
    return jsonify(result)


@score_bp.route("/calculate", methods=["POST"])
@jwt_required()
def calculate():
    farmer_id = int(get_jwt_identity())
    result = calculate_credit_score(farmer_id)
    return jsonify({"message": "Score calculated", **result})
