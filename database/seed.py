from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from database.db import db
from database.models import CropRecord, Farmer, Listing, Order, Review, Transaction


DEMO_FARMERS = [
    {
        "name": "Ramesh Patil",
        "phone": "9876543210",
        "password": "demo123",
        "aadhaar_last4": "4321",
        "state": "Maharashtra",
        "district": "Amravati",
        "village": "Karanja",
        "land_area_acres": 7.5,
        "land_type": "irrigated",
        "water_source": "borewell",
        "pm_kisan_id": "PMK-1001",
        "khasra_number": "KH-2201",
    },
    {
        "name": "Sita Yadav",
        "phone": "9876543211",
        "password": "demo123",
        "aadhaar_last4": "8765",
        "state": "Madhya Pradesh",
        "district": "Bhopal",
        "village": "Sehore",
        "land_area_acres": 5.4,
        "land_type": "rainfed",
        "water_source": "canal",
        "pm_kisan_id": "PMK-1002",
        "khasra_number": "KH-3302",
    },
    {
        "name": "Arjun Deshmukh",
        "phone": "9876543212",
        "password": "demo123",
        "aadhaar_last4": "1134",
        "state": "Maharashtra",
        "district": "Yavatmal",
        "village": "Wani",
        "land_area_acres": 9.2,
        "land_type": "irrigated",
        "water_source": "tube-well",
        "pm_kisan_id": "PMK-1003",
        "khasra_number": "KH-4403",
    },
]


DEMO_CROPS = [
    (1, "Soybean", "Rabi", 2024, 6.0, 14.0, 15.5, 12000, 9500, 8000, 1500, 1300, 4200, 65000, 50000),
    (1, "Cotton", "Kharif", 2023, 4.5, 18.0, 16.5, 10000, 7500, 6500, 1200, 1000, 5400, 89000, 64000),
    (2, "Wheat", "Rabi", 2024, 5.2, 22.0, 24.0, 11000, 7000, 5000, 1000, 900, 2150, 51600, 35000),
    (2, "Onion", "Kharif", 2023, 3.0, 11.0, 12.0, 9000, 6500, 4000, 800, 700, 1800, 21600, 15000),
    (3, "Soybean", "Kharif", 2024, 8.0, 13.5, 14.2, 14000, 9000, 9000, 2000, 1500, 4100, 58200, 42000),
]


DEMO_LISTINGS = [
    (1, "Soybean", 32.0, 4300, "Fresh soybean, cleaned and bagged", "Amravati", True, 8.0),
    (2, "Wheat", 18.0, 2200, "Good quality wheat from Bhopal", "Bhopal", False, 0),
    (3, "Onion", 25.0, 1900, "Stored onion available for quick dispatch", "Yavatmal", True, 6.0),
    (1, "Cotton", 14.0, 6400, "Premium cotton for textile buyers", "Amravati", True, 10.0),
    (2, "Soybean", 20.0, 4450, "Organic soybean in small pack sizes", "Sehore", False, 0),
]


def seed_demo_data():
    if Farmer.query.count() > 0:
        return

    for row in DEMO_FARMERS:
        farmer = Farmer(
            name=row["name"],
            phone=row["phone"],
            password=generate_password_hash(row["password"]),
            aadhaar_last4=row["aadhaar_last4"],
            state=row["state"],
            district=row["district"],
            village=row["village"],
            land_area_acres=row["land_area_acres"],
            land_type=row["land_type"],
            water_source=row["water_source"],
            pm_kisan_id=row["pm_kisan_id"],
            khasra_number=row["khasra_number"],
            created_at=datetime.utcnow(),
        )
        db.session.add(farmer)
    db.session.commit()

    farmers = Farmer.query.all()
    for farmer in farmers:
        for item in DEMO_CROPS:
            if item[0] == farmer.id:
                crop = CropRecord(
                    farmer_id=farmer.id,
                    crop_name=item[1],
                    season=item[2],
                    year=item[3],
                    area_sown_acres=item[4],
                    expected_yield_quintal=item[5],
                    actual_yield_quintal=item[6],
                    seed_cost=item[7],
                    fertilizer_cost=item[8],
                    labor_cost=item[9],
                    transport_cost=item[10],
                    other_cost=item[11],
                    selling_price_per_quintal=item[12],
                    total_revenue=item[13],
                    net_profit=item[14],
                )
                db.session.add(crop)

    for idx, item in enumerate(DEMO_LISTINGS, start=1):
        farmer_id, crop_name, quantity, price, description, location, transport_available, transport_cost = item
        listing = Listing(
            farmer_id=farmer_id,
            crop_name=crop_name,
            quantity_quintal=quantity,
            price_per_quintal=price,
            description=description,
            location=location,
            status="active",
            transport_available=transport_available,
            transport_cost_per_km=transport_cost,
            created_at=datetime.utcnow() - timedelta(days=idx),
            expires_at=datetime.utcnow() + timedelta(days=30),
        )
        db.session.add(listing)

    db.session.commit()

    for farmer in farmers:
        db.session.add(Transaction(farmer_id=farmer.id, type="sale", amount=25000 + farmer.id * 1000, description="Demo crop sale"))
        db.session.add(Transaction(farmer_id=farmer.id, type="loan_payment", amount=1200, description="Season repayment"))

    db.session.commit()

    # Create a couple of sample reviews and orders so the marketplace feels populated.
    listings = Listing.query.all()
    if listings:
        order = Order(
            listing_id=listings[0].id,
            buyer_farmer_id=farmers[1].id if len(farmers) > 1 else farmers[0].id,
            quantity=5,
            total_amount=5 * listings[0].price_per_quintal,
            escrow_status="held",
            razorpay_order_id="rzp_demo_001",
            status="confirmed",
        )
        db.session.add(order)
        db.session.commit()
        db.session.add(Review(reviewer_id=farmers[0].id, reviewee_id=listings[0].farmer_id, order_id=order.id, rating=4, comment="Good quality produce and timely support."))
        db.session.commit()