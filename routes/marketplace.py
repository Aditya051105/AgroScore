from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from database.db import db
from database.models import Farmer, Listing

market_bp = Blueprint("marketplace", __name__)


@market_bp.route("/listings", methods=["GET"])
def get_listings():
    crop = request.args.get("crop", "")
    district = request.args.get("district", "")
    listings = Listing.query.filter_by(status="active")
    if crop:
        listings = listings.filter(Listing.crop_name.ilike(f"%{crop}%"))
    if district:
        listings = listings.filter(Listing.location.ilike(f"%{district}%"))
    result = []
    for item in listings.order_by(Listing.created_at.desc()).all():
        farmer = Farmer.query.get(item.farmer_id)
        qty_kg = item.quantity_kg or (item.quantity_quintal * 100)
        price_kg = item.price_per_kg or (item.price_per_quintal / 100)
        result.append({
            "id": item.id,
            "crop_name": item.crop_name,
            "quantity_quintal": item.quantity_quintal,
            "quantity_kg": qty_kg,
            "price_per_quintal": item.price_per_quintal,
            "price_per_kg": price_kg,
            "description": item.description,
            "location": item.location or (farmer.district if farmer else ""),
            "farmer_name": farmer.name if farmer else "Farmer",
            "transport_available": item.transport_available,
            "transport_cost_per_km": item.transport_cost_per_km,
            "status": item.status,
        })
    return jsonify(result)


@market_bp.route("/listings", methods=["POST"])
@jwt_required()
def create_listing():
    farmer_id = int(get_jwt_identity())
    data = request.get_json() or {}
    quantity_quintal = float(data.get("quantity_quintal", 0) or 0)
    quantity_kg = float(data.get("quantity_kg", quantity_quintal * 100) or 0)
    price_per_quintal = float(data.get("price_per_quintal", 0) or 0)
    price_per_kg = float(data.get("price_per_kg", price_per_quintal / 100) or 0)

    listing = Listing(
        farmer_id=farmer_id,
        crop_name=data.get("crop_name", ""),
        quantity_quintal=quantity_quintal,
        quantity_kg=quantity_kg,
        price_per_quintal=price_per_quintal,
        price_per_kg=price_per_kg,
        description=data.get("description", ""),
        location=data.get("location", ""),
        transport_available=bool(data.get("transport_available", False)),
        transport_cost_per_km=float(data.get("transport_cost_per_km", 0) or 0),
        status="active",
    )
    db.session.add(listing)
    db.session.commit()
    return jsonify({"message": "Listing created", "listing_id": listing.id, "price_per_kg": price_per_kg, "quantity_kg": quantity_kg})

