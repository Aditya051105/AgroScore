from flask import Blueprint
from flask import request
from flask import jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from database.db import db
from database.models import CropRecord

crop_bp = Blueprint(
    "crops",
    __name__
)


@crop_bp.route(
    "/add",
    methods=["POST"]
)
@jwt_required()
def add_crop():

    farmer_id = int(get_jwt_identity())

    data = request.get_json()

    total_cost = (
        float(data["seed_cost"])
        + float(data["fertilizer_cost"])
        + float(data["labor_cost"])
        + float(data["transport_cost"])
        + float(data["other_cost"])
    )

    revenue = (
        float(
            data["actual_yield_quintal"]
        )
        *
        float(
            data["selling_price_per_quintal"]
        )
    )

    profit = revenue - total_cost

    crop = CropRecord(

        farmer_id=farmer_id,

        crop_name=data["crop_name"],

        season=data["season"],

        year=int(data["year"]),

        area_sown_acres=float(
            data["area_sown_acres"]
        ),

        expected_yield_quintal=float(
            data["expected_yield_quintal"]
        ),

        actual_yield_quintal=float(
            data["actual_yield_quintal"]
        ),

        seed_cost=float(
            data["seed_cost"]
        ),

        fertilizer_cost=float(
            data["fertilizer_cost"]
        ),

        labor_cost=float(
            data["labor_cost"]
        ),

        transport_cost=float(
            data["transport_cost"]
        ),

        other_cost=float(
            data["other_cost"]
        ),

        selling_price_per_quintal=float(
            data["selling_price_per_quintal"]
        ),

        total_revenue=revenue,

        net_profit=profit
    )

    db.session.add(crop)
    db.session.commit()

    return jsonify({
        "message": "Crop Added",
        "profit": profit
    })


@crop_bp.route(
    "/all",
    methods=["GET"]
)
@jwt_required()
def get_crops():

    farmer_id = int(get_jwt_identity())

    crops = CropRecord.query.filter_by(
        farmer_id=farmer_id
    ).all()

    result = []

    for crop in crops:

        result.append({
            "crop": crop.crop_name,
            "season": crop.season,
            "profit": crop.net_profit
        })

    return jsonify(result)