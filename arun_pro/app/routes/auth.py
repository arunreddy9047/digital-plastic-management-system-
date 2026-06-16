from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db
from app.i18n import translate

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@auth_bp.route('/login/<login_type>', methods=['GET', 'POST'])
def login(login_type='user'):
    login_type = 'admin' if login_type == 'admin' else 'user'

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            if login_type == 'admin' and not user.is_admin():
                flash(translate('admin_login_required'))
                return render_template('login.html', login_type=login_type)
            if login_type == 'user' and user.is_admin():
                flash(translate('user_login_required'))
                return render_template('login.html', login_type=login_type)

            login_user(user)
            flash(translate('login_successful'))
            return redirect(url_for('data.index'))
        else:
            flash(translate('wrong_username_or_password'))
    return render_template('login.html', login_type=login_type)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash(translate('username_exists'))
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, role='user')
            db.session.add(new_user)
            db.session.commit()
            flash(translate('account_created'))
            return redirect(url_for('auth.login', login_type='user'))
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(translate('logged_out'))
    return redirect(url_for('auth.login', login_type='user'))
