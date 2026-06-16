from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Event, EventRegistration
from datetime import datetime
from app.i18n import translate

events_bp = Blueprint('events', __name__)

@events_bp.route('/events')
@login_required
def events():
    all_events = Event.query.all()
    return render_template('events.html', events=all_events)

@events_bp.route('/events/register/<int:event_id>', methods=['GET', 'POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        registration = EventRegistration(
            event_id=event_id,
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            team_name=request.form['team_name'],
            registered_at=datetime.utcnow()
        )
        db.session.add(registration)
        db.session.commit()
        return redirect(url_for('events.registration_success', event_id=event_id))
    return render_template('event_register.html', event=event)

@events_bp.route('/events/success/<int:event_id>')
@login_required
def registration_success(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event_success.html', event=event)

@events_bp.route('/events/registrations/<int:event_id>')
@login_required
def view_registrations(event_id):
    if not current_user.is_admin():
        return redirect(url_for('events.events'))
    event = Event.query.get_or_404(event_id)
    registrations = EventRegistration.query.filter_by(event_id=event_id).all()
    return render_template(
        'event_registrations.html',
        event=event,
        registrations=registrations
    )

@events_bp.route('/api/add-event', methods=['POST'])
@login_required
def add_event():
    data = request.json
    try:
        event = Event(
            name=data['name'],
            event_date=data['event_date'],
            description=data['description'],
            is_fixed=False
        )
        db.session.add(event)
        db.session.commit()
        return jsonify({'message': translate('event_added_successfully')})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': translate('failed_to_add_event', error=str(e))}), 400

@events_bp.route('/api/delete-event/<int:id>', methods=['DELETE'])
@login_required
def delete_event(id):
    if not current_user.is_admin():
        return jsonify({'message': translate('admin_access_only')}), 403
    event = Event.query.get(id)
    if event:
        if event.is_fixed:
            return jsonify({'message': translate('cannot_delete_fixed_event')}), 400
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': translate('event_deleted_successfully')})
    return jsonify({'message': translate('event_not_found')}), 404
