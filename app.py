import os
from datetime import datetime, timedelta

from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request

from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required

from config import Config
from database.db import db
from database.seed import seed_demo_data
from routes.auth import auth_bp
from routes.crops import crop_bp
from routes.farmer import farmer_bp
from routes.marketplace import market_bp
from routes.orders import orders_bp
from routes.reviews import reviews_bp
from routes.score import score_bp
from database.models import CropRecord, Farmer, Listing, Order
from services.mandi_service import get_mandi_price
from services.weather_service import get_weather_for_district
app = Flask(__name__)

app.config.from_object(Config)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "agroscore.db")

os.makedirs(app.instance_path, exist_ok=True)

db.init_app(app)

jwt = JWTManager(app)

with app.app_context():
    db_path = os.path.join(app.instance_path, "agroscore.db")
   # if os.path.exists(db_path):
    #    os.remove(db_path)
    db.create_all()
    seed_demo_data()

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(crop_bp, url_prefix="/api/crops")
app.register_blueprint(farmer_bp, url_prefix="/api/farmer")
app.register_blueprint(market_bp, url_prefix="/api")
app.register_blueprint(orders_bp, url_prefix="/api/orders")
app.register_blueprint(reviews_bp, url_prefix="/api/reviews")
app.register_blueprint(score_bp, url_prefix="/api/score")
@app.route("/")
@app.route("/login")
def home():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/crops")
def crops():
    return render_template("crops.html")


@app.route("/score")
def score_page():
    return render_template("score.html")


@app.route("/marketplace-buy")
def marketplace_buy():
    return render_template("marketplace_buy.html")


@app.route("/marketplace-sell")
def marketplace_sell():
    return render_template("marketplace_sell.html")


@app.route("/orders")
def orders_page():
    return render_template("orders.html")


@app.route("/profile")
def profile_page():
    return render_template("profile.html")


@app.route("/insights")
def insights_page():
    return render_template("insights.html")


@app.route("/api/dashboard/analytics")
def dashboard_analytics():
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=6)

    orders = Order.query.order_by(Order.created_at.desc()).all()
    listings = Listing.query.order_by(Listing.created_at.desc()).all()
    crop_rows = CropRecord.query.order_by(CropRecord.id.desc()).all()

    selling_series = [0] * 7
    buying_series = [0] * 7

    for order in orders:
        order_date = order.created_at.date() if order.created_at else today
        if start_date <= order_date <= today:
            idx = (order_date - start_date).days
            selling_series[idx] += float(order.total_amount or 0)

    for listing in listings:
        listing_date = listing.created_at.date() if listing.created_at else today
        if start_date <= listing_date <= today:
            idx = (listing_date - start_date).days
            estimated_value = float(listing.quantity_kg or 0) * float(listing.price_per_kg or (listing.price_per_quintal / 100 if listing.price_per_quintal else 0))
            buying_series[idx] += estimated_value

    profit_labels = [crop.crop_name or f'Crop {i + 1}' for i, crop in enumerate(crop_rows[:6])]
    profit_series = [float(crop.net_profit or 0) for crop in crop_rows[:6]]

    if not any(selling_series):
        selling_series = [1200, 1450, 1600, 1350, 1700, 1880, 2100]
    if not any(buying_series):
        buying_series = [900, 1100, 1300, 1250, 1500, 1600, 1450]
    if not profit_series:
        profit_series = [12000, 18200, 22400, 21000, 26000, 31000]
        profit_labels = ['Wheat', 'Soybean', 'Cotton', 'Onion', 'Maize', 'Paddy']

    insights = [
        f"{len(listings)} active crop listings are currently available for market buyers.",
        f"{len(orders)} recent orders are tracked with payment and order IDs for follow-up.",
        f"Profit trend is strongest in {profit_labels[0] if profit_labels else 'recent crops'} with ₹{max(profit_series):,} in recorded profit.",
    ]

    return jsonify({
        "labels": [day.strftime("%a %d") for day in [start_date + timedelta(days=i) for i in range(7)]],
        "selling_series": selling_series,
        "buying_series": buying_series,
        "profit_labels": profit_labels,
        "profit_series": profit_series,
        "insights": insights,
        "total_orders": len(orders),
        "active_listings": len(listings),
        "total_profit": sum(profit_series),
    })


@app.route("/api/inventory", methods=["GET"])
def inventory_api():
    listings = Listing.query.order_by(Listing.created_at.desc()).limit(12).all()
    result = []
    for item in listings:
        farmer = Farmer.query.get(item.farmer_id)
        qty_kg = item.quantity_kg or (item.quantity_quintal * 100)
        result.append({
            "id": item.id,
            "crop_name": item.crop_name,
            "quantity_quintal": item.quantity_quintal,
            "quantity_kg": qty_kg,
            "price_per_quintal": item.price_per_quintal,
            "price_per_kg": item.price_per_kg or (item.price_per_quintal / 100 if item.price_per_quintal else 0),
            "location": item.location or (farmer.district if farmer else ""),
            "description": item.description,
            "status": item.status,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        })
    return jsonify(result)


@app.route("/api/inventory", methods=["POST"])
@jwt_required()
def add_inventory():
    farmer_id = int(get_jwt_identity())
    data = request.get_json() or {}
    quantity_quintal = float(data.get("quantity_quintal", 0) or 0)
    quantity_kg = float(data.get("quantity_kg", quantity_quintal * 100) or 0)
    price_per_quintal = float(data.get("price_per_quintal", 0) or 0)
    price_per_kg = float(data.get("price_per_kg", price_per_quintal / 100) or 0)

    listing = Listing(
        farmer_id=farmer_id,
        crop_name=data.get("crop_name", "").strip() or "Crop",
        quantity_quintal=quantity_quintal,
        quantity_kg=quantity_kg,
        price_per_quintal=price_per_quintal,
        price_per_kg=price_per_kg,
        description=data.get("description", "Manual inventory entry"),
        location=data.get("location", ""),
        transport_available=bool(data.get("transport_available", False)),
        transport_cost_per_km=float(data.get("transport_cost_per_km", 0) or 0),
        status="active",
    )
    db.session.add(listing)
    db.session.commit()
    return jsonify({"message": "Inventory item added", "listing_id": listing.id})


@app.route("/api/weather")
def weather_api():
    district = request.args.get("district", "Amravati")
    return jsonify(get_weather_for_district(district))


@app.route("/api/market/prices")
def market_prices_api():
    crop = request.args.get("crop", "wheat")
    district = request.args.get("district", "Amravati")
    return jsonify(get_mandi_price(crop, district))

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)