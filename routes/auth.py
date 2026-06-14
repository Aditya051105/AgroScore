from flask import Blueprint
from flask import request
from flask import jsonify

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from flask_jwt_extended import (
    create_access_token
)

from database.db import db
from database.models import Farmer

auth_bp = Blueprint(
    "auth",
    __name__
)


@auth_bp.route(
    "/register",
    methods=["POST"]
)
def register():

    data = request.get_json()

    farmer = Farmer.query.filter_by(
        phone=data["phone"]
    ).first()

    if farmer:
        return jsonify({
            "message": "Phone already exists"
        }), 400

    new_farmer = Farmer(

        name=data["name"],

        phone=data["phone"],

        password=generate_password_hash(
            data["password"]
        ),

        aadhaar_last4=data["aadhaar_last4"],

        state=data["state"],

        district=data["district"],

        village=data["village"],

        land_area_acres=float(
            data["land_area_acres"]
        ),

        land_type=data["land_type"],

        water_source=data["water_source"]
    )

    db.session.add(new_farmer)
    db.session.commit()

    return jsonify({
        "success": True,
        "message":
        "Registration Successful"
    })


@auth_bp.route(
    "/login",
    methods=["POST"]
)
def login():

    data = request.get_json()

    farmer = Farmer.query.filter_by(
        phone=data["phone"]
    ).first()

    if not farmer:
        return jsonify({
            "message": "User not found"
        }), 404

    if not check_password_hash(
        farmer.password,
        data["password"]
    ):
        return jsonify({
            "message": "Wrong password"
        }), 401

    token = create_access_token(
        identity=str(farmer.id)
    )

    return jsonify({
        "token": token,
        "farmer_id": farmer.id,
        "name": farmer.name
    })