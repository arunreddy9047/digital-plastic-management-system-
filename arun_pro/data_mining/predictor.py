import math
from datetime import datetime

from app.models import Location, WasteRecord


def _build_future_months(base_year, base_month, count=3):
    future_months = []
    for offset in range(1, count + 1):
        month = base_month + offset
        year = base_year
        while month > 12:
            month -= 12
            year += 1
        future_months.append((year, month, f"{year}-{month:02d}"))
    return future_months


def _month_number(year, month):
    return year * 12 + month


def _simple_projection(values, future_months):
    if not values:
        return []

    average = sum(values) / len(values)
    predictions = []
    for idx, (_, _, month_label) in enumerate(future_months, start=1):
        value = average * (1 + 0.03 * idx) + (2 * math.sin(idx))
        predictions.append({
            "month": month_label,
            "predicted_kg": max(0.1, round(value, 2))
        })
    return predictions


def _linear_regression_projection(monthly_totals, future_months):
    points = sorted(monthly_totals.items())
    if len(points) < 2:
        return _simple_projection(list(monthly_totals.values()), future_months)

    x_values = [point[0] for point in points]
    y_values = [point[1] for point in points]

    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(y_values) / len(y_values)

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)

    if denominator == 0:
        return _simple_projection(y_values, future_months)

    slope = numerator / denominator
    intercept = y_mean - (slope * x_mean)

    predictions = []
    for year, month, month_label in future_months:
        future_x = _month_number(year, month)
        predicted = (slope * future_x) + intercept
        predictions.append({
            "month": month_label,
            "predicted_kg": max(0.1, round(float(predicted), 2))
        })
    return predictions


def forecast():
    locations = Location.query.all()
    results = []

    last_record = WasteRecord.query.order_by(WasteRecord.recorded_date.desc()).first()
    if last_record:
        base_year = last_record.recorded_date.year
        base_month = last_record.recorded_date.month
    else:
        now = datetime.now()
        base_year = now.year
        base_month = now.month

    future_months = _build_future_months(base_year, base_month)

    for location in locations:
        records = WasteRecord.query.filter_by(location_id=location.id).all()
        if not records:
            continue

        monthly_totals = {}
        for record in records:
            month_key = _month_number(record.recorded_date.year, record.recorded_date.month)
            monthly_totals[month_key] = monthly_totals.get(month_key, 0.0) + float(record.quantity_kg)

        predictions = _linear_regression_projection(monthly_totals, future_months)
        if predictions:
            results.append({
                "district": location.name,
                "predictions": predictions
            })

    return results
