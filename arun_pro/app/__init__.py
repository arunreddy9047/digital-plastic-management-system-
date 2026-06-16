from flask import Flask, redirect, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from app.i18n import SUPPORTED_LANGUAGES, TRANSLATIONS, get_dynamic_labels, get_locale, localize_text, translate

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @app.context_processor
    def inject_i18n():
        return {
            't': translate,
            'localize': localize_text,
            'current_language': get_locale(),
            'supported_languages': SUPPORTED_LANGUAGES,
            'client_translations': TRANSLATIONS.get(get_locale(), TRANSLATIONS['en']),
            'client_dynamic_labels': get_dynamic_labels()
        }
    
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Blueprints
    from app.routes.data_entry import data_bp
    from app.routes.analysis import analysis_bp
    from app.routes.prediction import predict_bp
    from app.routes.auth import auth_bp
    from app.routes.nss import nss_bp
    from app.routes.events import events_bp
    report_bp = None
    try:
        from app.routes.report import report_bp
    except Exception as e:
        import traceback
        print("Warning: failed to import report_bp:", e)
        traceback.print_exc()
    
    app.register_blueprint(data_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(nss_bp)
    app.register_blueprint(events_bp)
    if report_bp is not None:
        app.register_blueprint(report_bp)

    @app.route('/set-language/<lang>')
    def set_language(lang):
        if lang in SUPPORTED_LANGUAGES:
            session['lang'] = lang
        return redirect(request.referrer or url_for('auth.login', login_type='user'))
    
    @click.command("create-user")
    @with_appcontext
    def create_user_cmd():
        username = input("Enter username: ")
        password = input("Enter password: ")
        role = input("Enter role (admin/user): ").lower()
        is_super = input("Is superadmin? (y/n): ").lower() == "y"
        
        user = User(
            username=username,
            password=generate_password_hash(password),
            role=role,
            is_superuser=is_super
        )
        db.session.add(user)
        db.session.commit()
        print(f"User {username} ({role}) created successfully!")
        
    app.cli.add_command(create_user_cmd, name="create-user")
    
    return app
