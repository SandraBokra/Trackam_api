import datetime
import uuid
from config.db import db

# Modèle de l'utilisateur
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(128), unique=True, default=lambda: str(uuid.uuid4()))
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), default="member")  # member, admin
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    password = db.Column(db.String(255), nullable=False)

    tasks = db.relationship('Task', backref='user', lazy=True)


# Modèle du projet
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(128), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default='active')  # active, completed, archived
    
    user_id = db.Column(db.String(128), db.ForeignKey('user.uid'), nullable=False)
    user = db.relationship('User', backref='projects')

    tasks = db.relationship('Task', backref='project', lazy=True)


# Modèle de la tâche
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
    project_id = db.Column(db.String(128), db.ForeignKey('project.uid'), nullable=False)

    # Relation One-to-Many entre Task et Tag
    tag_id = db.Column(db.String(128), db.ForeignKey('tag.uid'), nullable=True)
    tag = db.relationship('Tag', backref=db.backref('tasks_in_tag', lazy=True))  # Changer le backref ici



# Modèle du commentaire
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(128), unique=True, default=lambda: str(uuid.uuid4()))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    task_id = db.Column(db.String(128), db.ForeignKey('task.uid'), nullable=False)
    user_id = db.Column(db.String(128), db.ForeignKey('user.uid'), nullable=False)
    user = db.relationship('User', backref='comments')


# Modèle du tag
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(128), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(128), unique=True)

    # Lien inverse des tâches associées (changer le backref ici)
    tasks = db.relationship('Task', backref='tag_association', lazy=True)  # Nomme le backref différemment

