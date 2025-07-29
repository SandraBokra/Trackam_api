import datetime
from flask import request, jsonify
from models.trackam import Project
from config.db import db


def CreateProject():
    data = request.get_json()
    name = data.get("name")
    description = data.get("description")
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")
    user_id = data.get("user_id")

    if not name or not description or not start_date_str or not end_date_str or not user_id:
        return {"message": "Tous les champs sont requis"}, 400

    try:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        return {"message": "Format de date invalide. Utilisez YYYY-MM-DD"}, 400

    new_project = Project(
        name=name,
        description=description,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id
    )
    db.session.add(new_project)
    db.session.commit()

    return {"message": "Projet créé", "uid": new_project.uid}, 201


def GetAllProjects():
    projects = Project.query.all()
    data = [
        {
            "uid": p.uid,
            "name": p.name,
            "description": p.description,
            "start_date": p.start_date.strftime("%Y-%m-%d"),
            "end_date": p.end_date.strftime("%Y-%m-%d") if p.end_date else None,
        }
        for p in projects
    ]
    return data, 200


def GetSingleProject():
    project_id = request.json.get("uid")
    if not project_id:
        return {"message": "ID requis"}, 400

    project = Project.query.filter_by(uid=project_id).first()
    if not project:
        return {"message": "Projet non trouvé"}, 404

    data = {
        "uid": project.uid,
        "name": project.name,
        "description": project.description,
        "start_date": project.start_date.strftime("%Y-%m-%d"),
        "end_date": project.end_date.strftime("%Y-%m-%d") if project.end_date else None,
    }
    return jsonify(data), 200


def UpdateProject():
    project_id = request.json.get("uid")
    if not project_id:
        return {"message": "ID requis"}, 400

    up_project = Project.query.filter_by(uid=project_id).first()
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


def DeleteProject():
    print("Request JSON reçue :", request.json)
    project_id = request.json.get("uid")
    if not project_id:
        return {"message": "UID requis"}, 400

    project = Project.query.filter_by(uid=project_id).first()
    if not project:
        return {"message": "Projet non trouvé"}, 404

    db.session.delete(project)
    db.session.commit()
    return {"message": "Projet supprimé"}


def GetAllProjectsByUserId():
    data = request.get_json()
    print("Données reçues dans backend:", data)
    user_id = data.get("user_id")
    if not user_id:
        return {"message": "user_id requis"}, 400

    projects = Project.query.filter_by(user_id=user_id).order_by(Project.start_date.desc()).all()

    result = [
        {
            "uid": p.uid,
            "name": p.name,
            "description": p.description,
            "start_date": p.start_date.strftime("%Y-%m-%d"),
            "end_date": p.end_date.strftime("%Y-%m-%d") if p.end_date else None,
            "status": p.status
        }
        for p in projects
    ]

    return result, 200
