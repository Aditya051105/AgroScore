from database.db import db
from datetime import datetime


class Farmer(db.Model):
    __tablename__ = "farmers"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    phone = db.Column(db.String(20), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    aadhaar_last4 = db.Column(db.String(4))

    state = db.Column(db.String(50))

    district = db.Column(db.String(50))

    village = db.Column(db.String(50))

    land_area_acres = db.Column(db.Float)

    land_type = db.Column(db.String(50))

    water_source = db.Column(db.String(50))

    pm_kisan_id = db.Column(db.String(50), nullable=True)
    khasra_number = db.Column(db.String(50), nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class CropRecord(db.Model):
    __tablename__ = "crop_records"

    id = db.Column(db.Integer, primary_key=True)

    farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("farmers.id")
    )

    crop_name = db.Column(db.String(50))

    season = db.Column(db.String(20))

    year = db.Column(db.Integer)

    area_sown_acres = db.Column(db.Float)

    expected_yield_quintal = db.Column(db.Float)

    actual_yield_quintal = db.Column(db.Float)

    seed_cost = db.Column(db.Float)

    fertilizer_cost = db.Column(db.Float)

    labor_cost = db.Column(db.Float)

    transport_cost = db.Column(db.Float)

    other_cost = db.Column(db.Float)

    selling_price_per_quintal = db.Column(db.Float)

    total_revenue = db.Column(db.Float)

    net_profit = db.Column(db.Float)


class CreditScore(db.Model):
    __tablename__ = "credit_scores"

    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=300)
    grade = db.Column(db.String(2), nullable=False, default="D")
    yield_score = db.Column(db.Float, default=0)
    profit_score = db.Column(db.Float, default=0)
    land_score = db.Column(db.Float, default=0)
    market_score = db.Column(db.Float, default=0)
    repayment_score = db.Column(db.Float, default=0)
    notes = db.Column(db.Text, default="")
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Listing(db.Model):
    __tablename__ = "listings"

    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"), nullable=False)
    crop_name = db.Column(db.String(100), nullable=False)
    quantity_quintal = db.Column(db.Float, nullable=False, default=0)
    quantity_kg = db.Column(db.Float, nullable=False, default=0)
    price_per_quintal = db.Column(db.Float, nullable=False, default=0)
    price_per_kg = db.Column(db.Float, nullable=False, default=0)
    description = db.Column(db.Text, default="")
    location = db.Column(db.String(100), default="")
    status = db.Column(db.String(20), default="active")
    transport_available = db.Column(db.Boolean, default=False)
    transport_cost_per_km = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    diversification_score = db.Column(db.Float, default=0)

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey("listings.id"), nullable=False)
    buyer_farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0)
    quantity_kg = db.Column(db.Float, nullable=False, default=0)
    quantity_quintal = db.Column(db.Float, nullable=False, default=0)
    price_per_kg = db.Column(db.Float, nullable=False, default=0)
    price_per_quintal = db.Column(db.Float, nullable=False, default=0)
    total_amount = db.Column(db.Float, nullable=False, default=0)
    escrow_status = db.Column(db.String(20), default="held")
    razorpay_order_id = db.Column(db.String(100), default="")
    payment_id = db.Column(db.String(100), default="")
    status = db.Column(db.String(30), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey("farmers.id"), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)