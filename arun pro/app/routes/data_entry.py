from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import WasteRecord, Location, PlasticType, NSSTeam
from datetime import datetime
from decimal import Decimal
from app.i18n import translate

data_bp = Blueprint('data', __name__)

@data_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@data_bp.route('/entry')
@login_required
def entry():
    locations = Location.query.order_by(Location.name).all()
    plastic_types = PlasticType.query.all()
    nss_teams = NSSTeam.query.all()
    return render_template('entry.html', locations=locations, plastic_types=plastic_types, nss_teams=nss_teams)

@data_bp.route('/api/add-record', methods=['POST'])
@login_required
def add_record():
    data = request.json
    try:
        team_id = data.get('team_id')
        team_id = int(team_id) if team_id else None
        
        record = WasteRecord(
            location_id=int(data['location_id']),
            plastic_type_id=int(data['plastic_type_id']),
            quantity_kg=Decimal(str(data['quantity_kg'])),
            recorded_date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            recorded_by=data.get('recorded_by', 'Unknown'),
            team_id=team_id
        )
        db.session.add(record)
        db.session.commit()
        return jsonify({'message': translate('record_added_successfully')})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': translate('error_saving_record', error=str(e))}), 400

@data_bp.route('/records')
@login_required
def records():
    all_records = db.session.query(
        WasteRecord, Location.name, PlasticType.name
    ).join(Location, Location.id == WasteRecord.location_id
    ).join(PlasticType, PlasticType.id == WasteRecord.plastic_type_id).all()
    return render_template('records.html', records=all_records)

@data_bp.route('/api/delete-record/<int:id>', methods=['DELETE'])
@login_required
def delete_record(id):
    if not current_user.is_admin():
        return jsonify({'message': translate('admin_access_only')}), 403
    record = WasteRecord.query.get(id)
    if record:
        db.session.delete(record)
        db.session.commit()
        return jsonify({'message': translate('record_deleted_successfully')})
    return jsonify({'message': translate('record_not_found')}), 404

@data_bp.route('/api/edit-record/<int:id>', methods=['PUT'])
@login_required
def edit_record(id):
    if not current_user.is_admin():
        return jsonify({'message': translate('admin_access_only')}), 403
    record = WasteRecord.query.get(id)
    if record:
        data = request.json
        try:
            record.quantity_kg = Decimal(str(data['quantity_kg']))
            record.recorded_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            record.recorded_by = data.get('recorded_by', 'Unknown')
            db.session.commit()
            return jsonify({'message': translate('record_updated_successfully')})
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': translate('error_updating_record', error=str(e))}), 400
    return jsonify({'message': translate('record_not_found')}), 404
