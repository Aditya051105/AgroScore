from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from database.db import db
from database.models import Farmer, Review

reviews_bp = Blueprint("reviews", __name__)


@reviews_bp.route("", methods=["POST"])
@jwt_required()
def add_review():
    reviewer_id = int(get_jwt_identity())
    data = request.get_json() or {}
    review = Review(
        reviewer_id=reviewer_id,
        reviewee_id=int(data.get("reviewee_id")),
        order_id=data.get("order_id"),
        rating=int(data.get("rating", 5)),
        comment=data.get("comment", ""),
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({"message": "Review added"})


@reviews_bp.route("/<int:farmer_id>", methods=["GET"])
def get_reviews(farmer_id):
    reviews = Review.query.filter_by(reviewee_id=farmer_id).order_by(Review.created_at.desc()).all()
    farmer = Farmer.query.get(farmer_id)
    return jsonify({
        "farmer": farmer.name if farmer else "Farmer",
        "reviews": [{
            "id": item.id,
            "rating": item.rating,
            "comment": item.comment,
            "created_at": item.created_at.isoformat(),
        } for item in reviews],
    })
