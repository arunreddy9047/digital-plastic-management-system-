from flask import Blueprint, jsonify, render_template
from flask_login import login_required
from app import db
from app.models import WasteRecord, Location, PlasticType, Volunteer, NSSTeam
from sqlalchemy import func
from app.i18n import translate

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/dashboard')
@login_required
def dashboard():
    volunteer_count = db.session.query(func.count(Volunteer.id)).scalar() or 0
    team_count = db.session.query(func.count(NSSTeam.id)).scalar() or 0
    total_waste = db.session.query(func.sum(WasteRecord.quantity_kg)).scalar() or 0
    return render_template('dashboard.html', stats={
        'volunteers': volunteer_count,
        'teams': team_count,
        'waste': float(total_waste)
    })

@analysis_bp.route('/api/waste-by-location')
@login_required
def waste_by_location():
    results = db.session.query(
        Location.name,
        func.sum(WasteRecord.quantity_kg)
    ).join(WasteRecord, Location.id == WasteRecord.location_id
    ).group_by(Location.name).all()
    data = {row[0]: float(row[1]) for row in results}
    return jsonify(data)

@analysis_bp.route('/api/waste-by-type')
@login_required
def waste_by_type():
    results = db.session.query(
        PlasticType.name,
        func.sum(WasteRecord.quantity_kg)
    ).join(WasteRecord, PlasticType.id == WasteRecord.plastic_type_id
    ).group_by(PlasticType.name).all()
    data = {row[0]: float(row[1]) for row in results}
    return jsonify(data)

@analysis_bp.route('/api/waste-over-time')
@login_required
def waste_over_time():
    # SQLite compatibility for date formatting
    results = db.session.query(
        func.strftime('%Y-%m', WasteRecord.recorded_date).label('month'),
        func.sum(WasteRecord.quantity_kg)
    ).group_by('month').order_by('month').all()
    data = {row[0]: float(row[1]) for row in results}
    return jsonify(data)

@analysis_bp.route('/api/recyclable-vs-nonrecyclable')
@login_required
def recyclable_vs_non():
    recyclable = db.session.query(
        func.sum(WasteRecord.quantity_kg)
    ).join(PlasticType, PlasticType.id == WasteRecord.plastic_type_id
    ).filter(PlasticType.recyclable == True).scalar() or 0
    non_recyclable = db.session.query(
        func.sum(WasteRecord.quantity_kg)
    ).join(PlasticType, PlasticType.id == WasteRecord.plastic_type_id
    ).filter(PlasticType.recyclable == False).scalar() or 0
    return jsonify({
        translate('recyclable'): float(recyclable),
        translate('non_recyclable'): float(non_recyclable)
    })

@analysis_bp.route('/api/waste-collected')
@login_required
def waste_collected():
    results = db.session.query(
        func.strftime('%Y-%m', WasteRecord.recorded_date).label('month'),
        func.sum(WasteRecord.quantity_kg)
    ).group_by('month').order_by('month').all()
    data = {row[0]: float(row[1]) for row in results}
    return jsonify(data)
