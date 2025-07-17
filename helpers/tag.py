import datetime
from flask_jwt_extended import jwt_required
from flask import request
from models.trackam import Tag, Task
from config.db import db


from flask import request
from models.trackam import Tag, Task
from config.db import db

def create_tag():
    data = request.get_json()

    name = data.get("name")
    task_ids = data.get("task_ids")

    if not name or not task_ids:
        return {"message": "Le nom du tag et les tâches associées sont requis"}, 400

    # Vérifie que le tag n'existe pas déjà
    if Tag.query.filter_by(name=name.strip()).first():
        return {"message": "Ce tag existe déjà"}, 409

    # Récupère les tâches à partir des IDs fournis
    tasks = Task.query.filter(Task.id.in_(task_ids)).all()

    if not tasks:
        return {"message": "Aucune tâche trouvée avec les IDs donnés"}, 404

    new_tag = Tag(name=name.strip())
    new_tag.tasks = tasks

    db.session.add(new_tag)
    db.session.commit()

    return {
        "message": "Tag créé avec succès",
        "tag": {
            "id": new_tag.id,
            "name": new_tag.name,
            "tasks": [{"id": t.id, "titre": t.title} for t in new_tag.tasks]
        }
    }, 201


def get_all_tags():
    tags = Tag.query.all()

    result = []
    for tag in tags:
        result.append({
            'id': tag.id,
            'name': tag.name,
            'tasks': [{'id': task.id, 'titre': task.title} for task in tag.tasks]
        })

    return {"tags": result}, 200



def get_tag():
    tag_id = request.args.get("id")
    if not tag_id:
        return {"message": "ID requis"}, 400

    tag = Tag.query.filter_by(id=tag_id).first()
    if not tag:
        return {"message": "Tag non trouvé"}, 404

    return ({"tag": {
        'id': tag.id,
        'name': tag.name,
        'tasks': [{'id': task.id, 'titre': task.title} for task in tag.tasks]
    }}, 200)


def delete_tag():
    tag_id = request.args.get("id")
    if not tag_id:
        return {"message": "ID requis"}, 400

    new_tag = Tag.query.filter_by(id=tag_id).first()
    if not new_tag:
        return {"message": "Tag non trouvé"}, 404

    db.session.delete(new_tag)
    db.session.commit()
    return {"message": "Tag supprimé"}



def update_tag():
    tag_id = request.args.get("id")  
    if not tag_id:
        return {"message": "ID du tag requis"}, 400

    data = request.get_json()
    name = data.get("name")
    task_ids = data.get("task_ids")

    tag = Tag.query.get(tag_id)
    if not tag:
        return {"message": "Tag introuvable"}, 404

    if name:
        tag.name = name.strip()

    if task_ids is not None:
        tasks = []
        for id in task_ids:
            task = Task.query.get(id)
            if task:
                tasks.append(task)
        if not tasks:
            return {"message": "Aucune tâche valide trouvée pour associer au tag"}, 404
        tag.tasks = tasks

    db.session.commit()
    return {"message": "Tag mis à jour avec succès"}, 200
