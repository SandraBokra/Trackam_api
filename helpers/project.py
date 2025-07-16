import datetime
from flask import request
from models.trackam import Project
from config.db import db


def create_project():
    data = request.get_json()
    name = data.get("name")
    description = data.get("description")
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")

    if not name or not description or not start_date_str or not end_date_str:
        return {"message": "Tous les champs sont requis"}, 400

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        return {"message": "Format de date invalide. Utilisez YYYY-MM-DD"}, 400

    new_project = Project(name=name, description=description, start_date=start_date, end_date=end_date)
    db.session.add(new_project)
    db.session.commit()
    return {"message": "Projet créé", "id": new_project.id}, 201


def get_all_projects():
    projects = Project.query.all()
    return [
        {"id": p.id, 
         "name": p.name, 
         "description": p.description, 
         "start_date": p.start_date.strftime("%Y-%m-%d"),
         "end_date": p.end_date.strftime("%Y-%m-%d") if p.end_date else None,

        }
        for p in projects
    ]

def update_project():
    project_id = request.args.get("id")
    if not project_id:
        return {"message": "ID requis"}, 400

    up_project = Project.query.get(project_id)
    if not up_project:
        return {"message": "Projet non trouvé"}, 404

    data = request.get_json()
    up_project.name = data.get("name", up_project.name)
    up_project.description = data.get("description", up_project.description)

    if "start_date" in data:
        try:
            up_project.start_date = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d")
        except ValueError:
            return {"message": "Date de début invalide. Utilisez YYYY-MM-DD"}, 400

    if "end_date" in data:
        try:
            up_project.end_date = datetime.datetime.strptime(data["end_date"], "%Y-%m-%d")
        except ValueError:
            return {"message": "Date de fin invalide. Utilisez YYYY-MM-DD"}, 400

    db.session.commit()

    return {"message": "Mise à jour réussie"}

def delete_project():
    project_id = request.args.get("id")
    if not project_id:
        return {"message": "ID requis"}, 400

    new_project = Project.query.get(project_id)
    if not new_project:
        return {"message": "Projet non trouvé"}, 404

    db.session.delete(new_project)
    db.session.commit()
    return {"message": "Projet supprimé"}