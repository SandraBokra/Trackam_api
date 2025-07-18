import datetime
import uuid
from config.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(128), unique=True, default=lambda: str(uuid.uuid4()))
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), default="member")  # member, admin
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    password=db.Column(db.String(255), nullable=False)
    
    tasks = db.relationship('Task', backref='user', lazy=True)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(128), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default='active')  # active, completed, archived

    tasks = db.relationship('Task', backref='project', lazy=True)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(128), unique=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, done, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    assigned_to = db.Column(db.String(128), db.ForeignKey('user.uid'), nullable=False)
    tag_id = db.Column(db.String(128), db.ForeignKey('tag.uid'), nullable=False)
    project_id = db.Column(db.String(128), db.ForeignKey('project.uid'), nullable=False)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(128), unique=True, default=lambda: str(uuid.uuid4()))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    task_id = db.Column(db.String(128), db.ForeignKey('task.uid'), nullable=False)
    user_id = db.Column(db.String(128), db.ForeignKey('user.uid'), nullable=False)
    user = db.relationship('User', backref='comments')


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(128), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(128), unique=True)

    tasks = db.relationship('Task', backref=db.backref('tags', lazy='dynamic'))