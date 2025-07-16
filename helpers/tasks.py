from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.trackam import db, Task, User, Project, Tag
from datetime import datetime

# --- Création d'une tâche ---
@jwt_required()
def create_task():
    try:
        data = request.get_json()
        current_uid = get_jwt_identity()  # récupère l'UID utilisateur à partir du token
        current_user = User.query.filter_by(uid=current_uid).first()  # utilisateur connecté

        # Champs requis
        title = data.get('title')
        assigned_to_id = data.get('assigned_to')  # utilisateur à qui la tâche est assignée
        if not title or assigned_to_id is None:
            return jsonify({"message": "Les champs 'title' et 'assigned_to' sont obligatoires."}), 400

        # Si non-admin, ne peut s’assigner une tâche qu’à lui-même
        if current_user.role != "admin" and assigned_to_id != current_user.id:
            return jsonify({"message": "Vous ne pouvez créer une tâche que pour vous-même."}), 403

        # Vérifie que l'utilisateur assigné existe
        assigned_user = User.query.get(assigned_to_id)
        if not assigned_user:
            return jsonify({"message": "Utilisateur assigné non trouvé."}), 404

        # Vérifie que le projet existe (si fourni)
        project_id = data.get('project_id')
        if project_id:
            project = Project.query.get(project_id)
            if not project:
                return jsonify({"message": "Projet non trouvé."}), 404

        # Champs facultatifs
        description = data.get('description')
        status = data.get('status', 'pending')
        priority = data.get('priority', 'medium')
        due_date_str = data.get('due_date')
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.fromisoformat(due_date_str)
            except ValueError:
                return jsonify({"message": "Format date invalide (AAAA-MM-JJ)."}), 400

        # Création de la tâche
        new_task = Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            assigned_to=assigned_to_id,
            project_id=project_id
        )

        # Ajout de tags s’ils sont fournis
        tags_names = data.get('tags', [])
        for tag_name in tags_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                new_task.tags.append(tag)
            else:
                new_tag = Tag(name=tag_name)
                db.session.add(new_tag)
                new_task.tags.append(new_tag)

        db.session.add(new_task)
        db.session.commit()

        return jsonify({"message": "Tâche créée", "task_id": new_task.id}), 201

    except Exception as e:
        print("Erreur création tâche :", e)
        return jsonify({"message": "Erreur serveur"}), 500


# ------------------------------
# 🟡 LISTE DES TÂCHES
# ------------------------------
@jwt_required()
def get_tasks():
    try:
        current_uid = get_jwt_identity()
        current_user = User.query.filter_by(uid=current_uid).first()

        if current_user.role == "admin":
            tasks = Task.query.all()
        else:
            tasks = Task.query.filter_by(assigned_to=current_user.id).all()

        results = []
        for t in tasks:
            results.append({
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "assigned_to": t.assigned_to,
                "project_id": t.project_id,
                "tags": [tag.name for tag in t.tags]
            })

        return jsonify(results), 200

    except Exception as e:
        print("Erreur:", e)
        return jsonify({"message": "Erreur serveur"}), 500


# ------------------------------
# 🔵 DÉTAIL D'UNE TÂCHE
# ------------------------------
@jwt_required()
def get_task(task_id):
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"message": "Tâche non trouvée"}), 404

        current_uid = get_jwt_identity()
        current_user = User.query.filter_by(uid=current_uid).first()

        if current_user.role != "admin" and task.assigned_to != current_user.id:
            return jsonify({"message": "Accès refusé"}), 403

        result = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "assigned_to": task.assigned_to,
            "project_id": task.project_id,
            "tags": [tag.name for tag in task.tags]
        }

        return jsonify(result), 200

    except Exception as e:
        print("Erreur:", e)
        return jsonify({"message": "Erreur serveur"}), 500


# ------------------------------
# 🟣 MISE À JOUR D'UNE TÂCHE
# ------------------------------
@jwt_required()
def update_task(task_id):
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"message": "Tâche non trouvée"}), 404

        current_uid = get_jwt_identity()
        current_user = User.query.filter_by(uid=current_uid).first()

        # 🔒 Si non-admin, ne peut modifier QUE ses tâches
        if current_user.role != "admin" and task.assigned_to != current_user.id:
            return jsonify({"message": "Accès refusé"}), 403

        data = request.get_json()

        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.status = data.get('status', task.status)
        task.priority = data.get('priority', task.priority)

        due_date_str = data.get('due_date')
        if due_date_str:
            try:
                task.due_date = datetime.fromisoformat(due_date_str)
            except ValueError:
                return jsonify({"message": "Date invalide"}), 400

        project_id = data.get('project_id')
        if project_id:
            project = Project.query.get(project_id)
            if not project:
                return jsonify({"message": "Projet non trouvé"}), 404
            task.project_id = project_id

        assigned_to_id = data.get('assigned_to')
        if assigned_to_id:
            if current_user.role != "admin" and assigned_to_id != current_user.id:
                return jsonify({"message": "Vous ne pouvez réassigner cette tâche qu'à vous-même."}), 403
            user = User.query.get(assigned_to_id)
            if not user:
                return jsonify({"message": "Utilisateur assigné non trouvé"}), 404
            task.assigned_to = assigned_to_id

        tags_names = data.get('tags')
        if tags_names is not None:
            task.tags.clear()
            for name in tags_names:
                tag = Tag.query.filter_by(name=name).first()
                if tag:
                    task.tags.append(tag)
                else:
                    new_tag = Tag(name=name)
                    db.session.add(new_tag)
                    task.tags.append(new_tag)

        db.session.commit()
        return jsonify({"message": "Tâche mise à jour"}), 200

    except Exception as e:
        print("Erreur:", e)
        return jsonify({"message": "Erreur serveur"}), 500


# ------------------------------
# 🔴 SUPPRESSION D'UNE TÂCHE
# ------------------------------
@jwt_required()
def delete_task(task_id):
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"message": "Tâche non trouvée"}), 404

        current_uid = get_jwt_identity()
        current_user = User.query.filter_by(uid=current_uid).first()

        # 🔐 Seul un admin peut supprimer
        if current_user.role != "admin":
            return jsonify({"message": "Seuls les administrateurs peuvent supprimer une tâche."}), 403

        db.session.delete(task)
        db.session.commit()

        return jsonify({"message": "Tâche supprimée"}), 200

    except Exception as e:
        print("Erreur:", e)
        return jsonify({"message": "Erreur serveur"}), 500