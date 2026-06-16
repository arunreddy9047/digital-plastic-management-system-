from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # roles: 'admin', 'user'
    is_superuser = db.Column(db.Boolean, default=False)
    
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
        
    def is_super(self):
        return self.is_superuser

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))

class PlasticType(db.Model):
    __tablename__ = 'plastic_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    recyclable = db.Column(db.Boolean, default=True)

class NSSTeam(db.Model):
    __tablename__ = 'nss_teams'
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(100), nullable=False)
    team_leader = db.Column(db.String(100))
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    location = db.relationship('Location', backref='teams')
    enabled = db.Column(db.Boolean, default=True)
    volunteers = db.relationship('Volunteer', backref='team', lazy=True)

class Volunteer(db.Model):
    __tablename__ = 'volunteers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    team_id = db.Column(db.Integer, db.ForeignKey('nss_teams.id'))
    joined_date = db.Column(db.Date)
    task_assigned = db.Column(db.String(200), nullable=True)
    task_completed = db.Column(db.Boolean, default=False)
    enabled = db.Column(db.Boolean, default=True)
    contribution_type = db.Column(db.String(100))
    hours_worked = db.Column(db.Integer, default=0)
    impact = db.Column(db.String(200))

class WasteRecord(db.Model):
    __tablename__ = 'waste_records'
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    plastic_type_id = db.Column(db.Integer, db.ForeignKey('plastic_types.id'))
    quantity_kg = db.Column(db.Numeric(10, 2), nullable=False)
    recorded_date = db.Column(db.Date, nullable=False)
    recorded_by = db.Column(db.String(100))
    team_id = db.Column(db.Integer, db.ForeignKey('nss_teams.id'), nullable=True)
    
    location = db.relationship('Location', backref='waste_records')
    plastic_type = db.relationship('PlasticType', backref='waste_records')
    team = db.relationship('NSSTeam', backref='waste_records')

class WasteCollection(db.Model):
    __tablename__ = 'waste_collection'
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(20), nullable=False)
    collected_kg = db.Column(db.Integer, nullable=False)

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    event_date = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    is_fixed = db.Column(db.Boolean, default=False)
    registrations = db.relationship('EventRegistration', backref='event', lazy=True, cascade="all, delete-orphan")

class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    team_name = db.Column(db.String(100))
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
