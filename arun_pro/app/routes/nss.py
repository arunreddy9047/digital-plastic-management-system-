from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import NSSTeam, Volunteer, Location
from datetime import datetime
from app.i18n import translate

nss_bp = Blueprint('nss', __name__)

def parse_date(date_str):
    if not date_str:
        return None
    for fmt in ('%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}")

# --- NSS Teams ---

@nss_bp.route('/nss-teams')
@login_required
def nss_teams():
    teams = NSSTeam.query.all()
    locations = Location.query.order_by(Location.name).all()
    return render_template('nss_teams.html', teams=teams, locations=locations)

@nss_bp.route('/api/add-team', methods=['POST'])
@login_required
def add_team():
    data = request.json
    try:
        team = NSSTeam(
            team_name=data['team_name'],
            team_leader=data['team_leader'],
            location_id=int(data['location_id']) if data['location_id'] else None,
            enabled=True
        )
        db.session.add(team)
        db.session.commit()
        return jsonify({'message': translate('team_added_successfully')})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': translate('failed_to_add_team', error=str(e))}), 400

@nss_bp.route('/delete_team/<int:id>', methods=['POST'])
@login_required
def delete_team(id):
    if not current_user.is_admin():
        flash(translate('only_admins_can_delete_teams'))
        return redirect(url_for('nss.nss_teams'))
    team = NSSTeam.query.get_or_404(id)
    try:
        # Nullify reference in volunteers
        for vol in team.volunteers:
            vol.team_id = None
        db.session.delete(team)
        db.session.commit()
        flash(translate('team_deleted_successfully'))
    except Exception as e:
        db.session.rollback()
        flash(translate('error_deleting_team', error=str(e)))
    return redirect(url_for('nss.nss_teams'))

@nss_bp.route('/toggle_team/<int:team_id>/<int:status>', methods=['POST'])
@login_required
def toggle_team(team_id, status):
    if not current_user.is_admin():
        flash(translate('only_admins_can_toggle_teams'))
        return redirect(url_for('nss.nss_teams'))
    team = NSSTeam.query.get_or_404(team_id)
    team.enabled = bool(status)
    db.session.commit()
    flash(translate('team_toggle_message', team_name=team.team_name, status=translate('active' if team.enabled else 'disabled').lower()))
    return redirect(url_for('nss.nss_teams'))

@nss_bp.route('/edit_team/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_team(id):
    if not current_user.is_admin():
        flash(translate('only_admins_can_edit_teams'))
        return redirect(url_for('nss.nss_teams'))
    team = NSSTeam.query.get_or_404(id)
    if request.method == 'POST':
        team.team_name = request.form['team_name']
        team.team_leader = request.form['team_leader']
        loc_id = request.form.get('location_id')
        team.location_id = int(loc_id) if loc_id else None
        team.enabled = 'enabled' in request.form or request.form.get('enabled') == 'on'
        db.session.commit()
        flash(translate('team_updated_successfully'))
        return redirect(url_for('nss.nss_teams'))
    locations = Location.query.order_by(Location.name).all()
    return render_template('edit_team.html', team=team, locations=locations)


# --- Volunteers ---

@nss_bp.route('/volunteers')
@login_required
def volunteers():
    all_volunteers = Volunteer.query.all()
    teams = NSSTeam.query.all()
    return render_template('volunteer.html', volunteers=all_volunteers, teams=teams)

@nss_bp.route('/api/add-volunteer', methods=['POST'])
@login_required
def add_volunteer():
    data = request.json
    try:
        volunteer = Volunteer(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            team_id=int(data['team_id']) if data['team_id'] else None,
            joined_date=parse_date(data['joined_date']),
            contribution_type=data.get('contribution_type'),
            hours_worked=int(data.get('hours_worked') or 0),
            impact=data.get('impact'),
            task_completed=False,
            enabled=True
        )
        db.session.add(volunteer)
        db.session.commit()
        return jsonify({'message': translate('volunteer_added_successfully')})
    except Exception as e:
        db.session.rollback()
        print("Error adding volunteer:", e)
        return jsonify({'message': translate('failed_to_add_volunteer', error=str(e))}), 400

@nss_bp.route('/delete_volunteer/<int:id>', methods=['POST'])
@login_required
def delete_volunteer(id):
    if not current_user.is_admin():
        flash(translate('only_admins_can_delete_volunteers'))
        return redirect(url_for('nss.volunteers'))
    volunteer = Volunteer.query.get_or_404(id)
    db.session.delete(volunteer)
    db.session.commit()
    flash(translate('volunteer_deleted_successfully'))
    return redirect(url_for('nss.volunteers'))

@nss_bp.route('/edit_volunteer/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_volunteer(id):
    if not current_user.is_admin():
        flash(translate('only_admins_can_edit_volunteers'))
        return redirect(url_for('nss.volunteers'))
    volunteer = Volunteer.query.get_or_404(id)
    if request.method == 'POST':
        volunteer.name = request.form['name']
        volunteer.email = request.form['email']
        volunteer.phone = request.form['phone']
        volunteer.team_id = int(request.form['team_id']) if request.form['team_id'] else None
        volunteer.joined_date = parse_date(request.form['joined_date'])
        volunteer.contribution_type = request.form.get('contribution_type')
        volunteer.hours_worked = int(request.form.get('hours_worked') or 0)
        volunteer.impact = request.form.get('impact')
        db.session.commit()
        flash(translate('volunteer_updated_successfully'))
        return redirect(url_for('nss.volunteers'))
    teams = NSSTeam.query.all()
    return render_template('edit_volunteer.html', volunteer=volunteer, teams=teams)

@nss_bp.route('/certificate/<int:id>')
@login_required
def generate_certificate(id):
    volunteer = Volunteer.query.get_or_404(id)
    return render_template('certificate.html', volunteer=volunteer, auto_print=False)

@nss_bp.route('/download_certificate/<int:id>')
@login_required
def download_certificate(id):
    volunteer = Volunteer.query.get_or_404(id)
    return render_template('certificate.html', volunteer=volunteer, auto_print=True)
