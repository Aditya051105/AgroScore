from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from database.db import db
from database.models import Listing, Order

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("", methods=["GET"])
@jwt_required()
def get_orders():
    farmer_id = int(get_jwt_identity())
    rows = Order.query.filter((Order.buyer_farmer_id == farmer_id) | (Order.listing_id.in_([l.id for l in Listing.query.filter_by(farmer_id=farmer_id).all()]))).order_by(Order.created_at.desc()).all()
    return jsonify([{
        "id": item.id,
        "listing_id": item.listing_id,
        "buyer_farmer_id": item.buyer_farmer_id,
        "quantity": item.quantity,
        "quantity_kg": item.quantity_kg,
        "quantity_quintal": item.quantity_quintal,
        "price_per_kg": item.price_per_kg,
        "price_per_quintal": item.price_per_quintal,
        "total_amount": item.total_amount,
        "status": item.status,
        "escrow_status": item.escrow_status,
        "razorpay_order_id": item.razorpay_order_id,
        "payment_id": item.payment_id,
    } for item in rows])


@orders_bp.route("", methods=["POST"])
@jwt_required()
def create_order():
    buyer_farmer_id = int(get_jwt_identity())
    data = request.get_json() or {}
    listing = Listing.query.get(data.get("listing_id"))
    if not listing:
        return jsonify({"message": "Listing not found"}), 404
    quantity = float(data.get("quantity", 0) or 0)
    quantity_kg = float(data.get("quantity_kg", quantity * 100) or 0)
    quantity_quintal = float(data.get("quantity_quintal", quantity / 100) or 0)
    price_per_kg = float(data.get("price_per_kg", listing.price_per_kg or (listing.price_per_quintal / 100)) or 0)
    price_per_quintal = float(data.get("price_per_quintal", listing.price_per_quintal) or 0)
    total_amount = quantity_kg * price_per_kg if quantity_kg else quantity_quintal * price_per_quintal

    order = Order(
        listing_id=listing.id,
        buyer_farmer_id=buyer_farmer_id,
        quantity=quantity,
        quantity_kg=quantity_kg,
        quantity_quintal=quantity_quintal,
        price_per_kg=price_per_kg,
        price_per_quintal=price_per_quintal,
        total_amount=total_amount,
        razorpay_order_id=data.get("razorpay_order_id", "demo_order"),
        payment_id=data.get("payment_id", "demo_payment"),
        status=data.get("status", "confirmed"),
        escrow_status=data.get("escrow_status", "held"),
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({"message": "Order placed", "order_id": order.id, "total_amount": total_amount, "quantity_kg": quantity_kg, "price_per_kg": price_per_kg, "price_per_quintal": price_per_quintal})


@orders_bp.route("/<int:order_id>/status", methods=["PUT"])
@jwt_required()
def update_status(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json() or {}
    order.status = data.get("status", order.status)
    db.session.commit()
    return jsonify({"message": "Order status updated", "status": order.status})


@orders_bp.route("/<int:order_id>/confirm-delivery", methods=["PUT"])
@jwt_required()
def confirm_delivery(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = "delivered"
    order.escrow_status = "released"
    db.session.commit()
    return jsonify({"message": "Delivery confirmed", "status": order.status})
