from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app import db
from app.models import WasteRecord
from sqlalchemy import func
from data_mining.predictor import forecast

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/prediction')
@login_required
def prediction():
    return render_template('prediction.html')

@predict_bp.route('/api/forecast')
@login_required
def get_forecast():
    try:
        results = forecast()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@predict_bp.route('/api/past-waste')
@login_required
def past_waste():
    # Group past waste records by month (SQLite format)
    results = (
        db.session.query(
            func.strftime('%Y-%m', WasteRecord.recorded_date).label('month'),
            func.sum(WasteRecord.quantity_kg)
        )
        .group_by('month')
        .order_by('month')
        .all()
    )
    data = {row[0]: float(row[1]) for row in results}
    return jsonify(data)
