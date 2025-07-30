from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.trackam import *
from datetime import datetime


@jwt_required()
def create_task():
    try:
        # Récupérer l'email de l'utilisateur authentifié à partir du token JWT
        current_uid = get_jwt_identity()

        # Chercher l'utilisateur dans la base de données par email
        current_user = User.query.filter_by(email=current_uid).first()

        # Si l'utilisateur n'existe pas, renvoyer une erreur
        if not current_user:
            return {"message": "Utilisateur non trouvé ou non authentifié."}, 401

        title = request.json.get('title')
        assigned_to_uid = request.json.get('assigned_to')

        # Vérification des champs obligatoires
        if not title or assigned_to_uid is None:
            return {"message": "Les champs 'title' et 'assigned_to' sont obligatoires."}, 400

        # Vérification des permissions
        if current_user.role != "admin" and assigned_to_uid != current_user.uid:
            return {"message": "Vous ne pouvez créer une tâche que pour vous-même."}, 403

        # Vérifier si l'utilisateur assigné existe
        assigned_user = User.query.filter_by(uid=assigned_to_uid).first()
        if not assigned_user:
            return {"message": "Utilisateur assigné non trouvé."}, 404

        project_uid = request.json.get('project_id')
        if not project_uid:
            return {"message": "Le champ 'project_id' est obligatoire."}, 400

        project = Project.query.filter_by(uid=project_uid).first()
        if not project:
            return {"message": "Projet non trouvé."}, 404
        


        description = request.json.get('description')
        status = request.json.get('status', 'pending')  # Statut par défaut 'pending'
        priority = request.json.get('priority', 'medium')  # Priorité par défaut 'medium'

        due_date_str = request.json.get('due_date')
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.fromisoformat(due_date_str)
            except ValueError:
                return {"message": "Format date invalide (AAAA-MM-JJ)."}, 400

        # Création de la tâche
        new_task = Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            assigned_to=assigned_to_uid,  # Utilisation de uid
            project_id=project_uid  # Utilisation de uid
        )

        # Gestion des tags
        tag_name = request.json.get('tag')  # Assumons qu'il y a un seul tag par tâche

        if tag_name:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                new_task.tag_id = tag.uid  # Utilisation de tag_id pour relier la tâche au tag
            else:
                # Créer un nouveau tag si il n'existe pas
                new_tag = Tag(name=tag_name)
                db.session.add(new_tag)
                db.session.commit()  # Commit pour obtenir l'uid du tag créé
                new_task.tag_id = new_tag.uid  # Associer ce tag à la tâche

        db.session.add(new_task)
        db.session.commit()

        return {"message": "Tâche créée", "task_id": new_task.id}, 201
    except Exception as e:
        print("Erreur création tâche :", e)
        return {"message": "Erreur serveur"}, 500


@jwt_required()
def get_tasks():
    try:
        current_uid = get_jwt_identity()
        print(f"Utilisateur authentifié : {current_uid}")
        current_user = User.query.filter_by(email=current_uid).first()

        if not current_user:
            return {"message": "Utilisateur non trouvé ou non authentifié."}, 401

        if current_user.role == "admin":
            tasks = Task.query.all()
            nbre= Task.query.count()
        else:
            tasks = Task.query.filter_by(assigned_to=current_user.uid).all()
            nbre = Task.query.filter_by(assigned_to=current_user.uid).count()

        results = []
        for t in tasks:
            # ⬇️ ICI : utiliser t.tag_id et non tasks.tag_id
            tag = Tag.query.filter_by(uid=t.tag_id).first()
            tag_name = tag.name if tag else None

            results.append({
                "id": t.id,
                "uid": t.uid,
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "assigned_to": t.assigned_to,
                "project_id": t.project_id,
                "tag": tag_name,
                "nbre": nbre
            })

        return results, 200
    except Exception as e:
        print("Erreur:", e)
        return {"message": "Erreur serveur"}, 500



@jwt_required()
def get_task(task_id):
    try:
        task = Task.query.get(task_id)
        if not task:
            return {"message": "Tâche non trouvée"}, 404

        current_uid = get_jwt_identity()
        current_user = User.query.filter_by(email=current_uid).first()

        if current_user.role != "admin" and task.assigned_to != current_user.uid:  # Utilisation de uid
            return {"message": "Accès refusé"}, 403

        tag = Tag.query.filter_by(uid=t.tag_id).first() # type: ignore
        tag_name = tag.name if tag else None  # Vérifie si un tag existe

        result = {
            "id": task.id,
            "uid": task.uid,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "assigned_to": task.assigned_to,
            "project_id": task.project_id,
            "tag": tag_name  # Retourne un seul tag
        }

        return result, 200
    except Exception as e:
        print("Erreur:", e)
        return {"message": "Erreur serveur"}, 500


@jwt_required()
def update_task(task_id, data):
    try:
        task = Task.query.get(task_id)
        if not task:
            return {"message": "Tâche non trouvée"}, 404

        current_uid = get_jwt_identity()
        current_user = User.query.filter_by(email=current_uid).first()

        if current_user.role != "admin" and task.assigned_to != current_user.uid:
            return {"message": "Accès refusé"}, 403

        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.status = data.get('status', task.status)
        task.priority = data.get('priority', task.priority)

        due_date_str = data.get('due_date')
        if due_date_str:
            try:
                task.due_date = datetime.fromisoformat(due_date_str)
            except ValueError:
                return {"message": "Date invalide"}, 400

        project_uid = data.get('project_id')
        if project_uid:
            project = Project.query.filter_by(uid=project_uid).first()
            if not project:
                return {"message": "Projet non trouvé"}, 404
            task.project_id = project_uid

        assigned_to_uid = data.get('assigned_to')
        if assigned_to_uid:
            if current_user.role != "admin" and assigned_to_uid != current_user.uid:
                return {"message": "Vous ne pouvez réassigner cette tâche qu'à vous-même."}, 403
            user = User.query.filter_by(uid=assigned_to_uid).first()
            if not user:
                return {"message": "Utilisateur assigné non trouvé"}, 404
            task.assigned_to = assigned_to_uid

        tag_name = data.get('tag')
        if tag_name:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                task.tag_id = tag.uid
            else:
                new_tag = Tag(name=tag_name)
                db.session.add(new_tag)
                db.session.commit()
                task.tag_id = new_tag.uid

        db.session.commit()
        return {"message": "Tâche mise à jour"}, 200

    except Exception as e:
        print("Erreur:", e)
        return {"message": "Erreur serveur"}, 500



@jwt_required()
def delete_task(task_id):
    try:
        task = Task.query.get(task_id)
        if not task:
            return {"message": "Tâche non trouvée"}, 404

        db.session.delete(task)
        db.session.commit()
        return {"message": "Tâche supprimée avec succès."}, 200
    except Exception as e:
        print("Erreur:", e)
        return {"message": "Erreur serveur"}, 500


@jwt_required()
def update_task_status():
    try:
        data = request.get_json()
        task_id = data.get('uid')
        new_status = data.get('status')

        if not task_id or not new_status:
            return {"message": "Les champs 'uid' et 'status' sont requis."}, 400

        task = Task.query.filter_by(uid=task_id).first()
        if not task:
            return {"message": "Tâche non trouvée"}, 404

        current_uid = get_jwt_identity()
        current_user = User.query.filter_by(email=current_uid).first()

        if current_user.role != "admin" and task.assigned_to != current_user.uid:
            return {"message": "Accès refusé"}, 403

        task.status = new_status
        db.session.commit()

        return {"message": "Statut de la tâche mis à jour avec succès"}, 200

    except Exception as e:
        print("Erreur:", e)
        return {"message": "Erreur serveur"}, 500