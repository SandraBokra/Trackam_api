from flask_restful import Resource, reqparse
from flask import jsonify
from models.trackam import db, Task, User, Tag
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

task_parser = reqparse.RequestParser()
task_parser.add_argument('title', type=str, required=True)
task_parser.add_argument('description', type=str)
task_parser.add_argument('status', type=str, default='pending')
task_parser.add_argument('priority', type=str, default='medium')
task_parser.add_argument('due_date', type=str)
task_parser.add_argument('assigned_to', type=int, required=True)
task_parser.add_argument('project_id', type=int)
task_parser.add_argument('tags', type=list, location='json')  # liste de noms de tags

class TaskListResource(Resource):
    @jwt_required()
    def get(self):
        tasks = Task.query.all()
        return jsonify([{
            'id': t.id,
            'title': t.title,
            'status': t.status,
            'priority': t.priority,
            'assigned_to': t.assigned_to,
            'project_id': t.project_id,
            'tags': [tag.name for tag in t.tags]
        } for t in tasks])

    @jwt_required()
    def post(self):
        args = task_parser.parse_args()
        user = User.query.get(args['assigned_to'])
        if not user:
            return {'error': 'Utilisateur introuvable'}, 404

        try:
            due = datetime.strptime(args['due_date'], '%Y-%m-%d') if args['due_date'] else None
        except ValueError:
            return {'error': 'Date invalide. Format attendu : YYYY-MM-DD'}, 400

        task = Task(
            title=args['title'],
            description=args['description'],
            status=args['status'],
            priority=args['priority'],
            due_date=due,
            assigned_to=args['assigned_to'],
            project_id=args['project_id']
        )

        # Gérer les tags
        if args['tags']:
            for tag_name in args['tags']:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag:
                    task.tags.append(tag)

        db.session.add(task)
        db.session.commit()
        return {'message': 'Tâche créée'}, 201

class TaskResource(Resource):
    @jwt_required()
    def get(self, task_id):
        task = Task.query.get_or_404(task_id)
        return {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'due_date': str(task.due_date) if task.due_date else None,
            'assigned_to': task.assigned_to,
            'project_id': task.project_id,
            'tags': [tag.name for tag in task.tags]
        }

    @jwt_required()
    def put(self, task_id):
        task = Task.query.get_or_404(task_id)
        current_uid = get_jwt_identity()
        user = User.query.filter_by(uid=current_uid).first()

        if user.id != task.assigned_to and user.role != 'admin':
            return {'error': 'Accès refusé'}, 403

        args = task_parser.parse_args()
        task.title = args['title']
        task.description = args.get('description', task.description)
        task.status = args.get('status', task.status)
        task.priority = args.get('priority', task.priority)
        task.due_date = datetime.strptime(args['due_date'], '%Y-%m-%d') if args['due_date'] else task.due_date
        task.project_id = args.get('project_id', task.project_id)

        # Tags (remplacer entièrement la liste)
        task.tags.clear()
        if args['tags']:
            for tag_name in args['tags']:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag:
                    task.tags.append(tag)

        db.session.commit()
        return {'message': 'Tâche mise à jour'}, 200

    @jwt_required()
    def delete(self, task_id):
        task = Task.query.get_or_404(task_id)
        current_uid = get_jwt_identity()
        user = User.query.filter_by(uid=current_uid).first()

        if user.role != 'admin' and user.id != task.assigned_to:
            return {'error': 'Suppression refusée'}, 403

        db.session.delete(task)
        db.session.commit()
        return {'message': 'Tâche supprimée'}, 200
