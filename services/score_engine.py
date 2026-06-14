from datetime import datetime

import math

from database.db import db
from database.models import CropRecord, CreditScore, Farmer, Order, Review


DISTRICT_COST_AVERAGE = {
    "wheat": 1800,
    "soybean": 1400,
    "cotton": 2600,
    "onion": 3800,
    "tur": 1650,
    "maize": 1350,
    "paddy": 2000,
}


def calculate_credit_score(farmer_id):
    farmer = Farmer.query.get(farmer_id)
    crops = CropRecord.query.filter_by(farmer_id=farmer_id).order_by(CropRecord.year.desc()).all()

    if not farmer or not crops:
        return {
            "score": 300,
            "grade": "D",
            "yield_score": 0,
            "profit_score": 0,
            "land_score": 0,
            "market_score": 0,
            "repayment_score": 0,
            "notes": "Add crop records to start building your credit profile.",
        }

    yield_ratios = []
    profit_margins = []
    cost_scores = []
    total_costs = 0
    revenue_total = 0

    for crop in crops:
        expected = crop.expected_yield_quintal or 1
        actual = crop.actual_yield_quintal or 0
        yield_ratios.append(actual / expected if expected else 0)

        revenue = float(crop.total_revenue or (crop.actual_yield_quintal * crop.selling_price_per_quintal if crop.selling_price_per_quintal else 0))
        costs = float(crop.seed_cost or 0) + float(crop.fertilizer_cost or 0) + float(crop.labor_cost or 0) + float(crop.transport_cost or 0) + float(crop.other_cost or 0)
        total_costs += costs
        revenue_total += revenue
        margin = (revenue - costs) / revenue if revenue else 0
        profit_margins.append(margin)

        cost_per_acre = costs / (crop.area_sown_acres or 1)
        avg_cost = DISTRICT_COST_AVERAGE.get((crop.crop_name or "").lower(), 2000)
        cost_scores.append(10 if cost_per_acre < avg_cost else 5)

    avg_yield_ratio = sum(yield_ratios) / len(yield_ratios)
    yield_score = min(avg_yield_ratio * 25, 25)

    avg_margin = sum(profit_margins) / len(profit_margins)
    if avg_margin > 0.40:
        profit_score = 20
    elif avg_margin >= 0.20:
        profit_score = 15
    elif avg_margin >= 0:
        profit_score = 10
    else:
        profit_score = 5

    land_score = 15 if farmer.land_type == "irrigated" else 12 if farmer.water_source in ("canal", "borewell", "tube-well") else 8
    if farmer.land_area_acres and farmer.land_area_acres > 5:
        land_score += 3

    unique_crops = len(set(c.crop_name for c in crops if c.crop_name))
    if unique_crops >= 3:
        diversification_score = 10
    elif unique_crops == 2:
        diversification_score = 7
    else:
        diversification_score = 4

    completed_orders = Order.query.filter(Order.buyer_farmer_id == farmer_id, Order.status.in_(["confirmed", "delivered"])).count()
    review_rows = Review.query.filter_by(reviewee_id=farmer_id).all()
    avg_rating = (sum(r.rating for r in review_rows) / len(review_rows)) if review_rows else 4.25
    market_score = min(completed_orders * 2, 10) + min(int(avg_rating * 2), 10)

    cost_management_score = sum(cost_scores) / max(len(cost_scores), 1)
    repayment_score = min(10 + (len(crops) * 0.5), 10)

    raw_score = yield_score + profit_score + land_score + market_score + diversification_score + cost_management_score
    normalized_score = int(300 + (raw_score / 100) * 550)
    score = max(300, min(850, normalized_score))

    if score >= 700:
        grade = "A"
    elif score >= 550:
        grade = "B"
    elif score >= 400:
        grade = "C"
    else:
        grade = "D"

    existing = CreditScore.query.filter_by(farmer_id=farmer_id).order_by(CreditScore.calculated_at.desc()).first()
    if existing:
        existing.score = score
        existing.grade = grade
        existing.yield_score = round(yield_score, 2)
        existing.profit_score = round(profit_score, 2)
        existing.land_score = round(land_score, 2)
        existing.market_score = round(market_score, 2)
        existing.repayment_score = round(repayment_score, 2)
        existing.notes = "Score generated from recent yield, profit, land, market, and cost data."
        existing.calculated_at = datetime.utcnow()
        record = existing
    else:
        record = CreditScore(
            farmer_id=farmer_id,
            score=score,
            grade=grade,
            yield_score=round(yield_score, 2),
            profit_score=round(profit_score, 2),
            land_score=round(land_score, 2),
            market_score=round(market_score, 2),
            repayment_score=round(repayment_score, 2),
            notes="Score generated from recent yield, profit, land, market, and cost data.",
        )
        db.session.add(record)

    db.session.commit()

    return {
        "score": score,
        "grade": grade,
        "yield_score": round(yield_score, 2),
        "profit_score": round(profit_score, 2),
        "land_score": round(land_score, 2),
        "market_score": round(market_score, 2),
        "repayment_score": round(repayment_score, 2),
        "notes": "Score generated from recent yield, profit, land, market, and cost data.",
    }
