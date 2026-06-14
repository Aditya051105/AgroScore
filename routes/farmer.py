from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from database.db import db
from database.models import Farmer

farmer_bp = Blueprint("farmer", __name__)


@farmer_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    farmer_id = int(get_jwt_identity())
    farmer = Farmer.query.get(farmer_id)
    if not farmer:
        return jsonify({"message": "Farmer not found"}), 404

    return jsonify({
        "id": farmer.id,
        "name": farmer.name,
        "phone": farmer.phone,
        "aadhaar_last4": farmer.aadhaar_last4,
        "state": farmer.state,
        "district": farmer.district,
        "village": farmer.village,
        "land_area_acres": farmer.land_area_acres,
        "land_type": farmer.land_type,
        "water_source": farmer.water_source,
        "pm_kisan_id": farmer.pm_kisan_id,
        "khasra_number": farmer.khasra_number,
    })


@farmer_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    farmer_id = int(get_jwt_identity())
    farmer = Farmer.query.get(farmer_id)
    if not farmer:
        return jsonify({"message": "Farmer not found"}), 404

    data = request.get_json() or {}
    for key in ["name", "phone", "aadhaar_last4", "state", "district", "village", "land_type", "water_source", "pm_kisan_id", "khasra_number"]:
        if key in data:
            setattr(farmer, key, data[key])
    if "land_area_acres" in data:
        farmer.land_area_acres = float(data["land_area_acres"])

    db.session.commit()
    return jsonify({"message": "Profile updated", "farmer_id": farmer.id})
