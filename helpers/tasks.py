from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.trackam import db, Task, User, Project, Tag
from datetime import datetime


@jwt_required()
def create_task():
    try:
        data = request.get_json()
        current_uid = get_jwt_identity()
        current_user = User.query.filter_by(uid=current_uid).first()

        # Récupère le titre et l'ID de la personne assignée depuis les données reçues
        title = data.get('title')
        assigned_to_id = data.get('assigned_to')
        # Vérifie que le titre et la personne assignée sont bien présents
        if not title or assigned_to_id is None:
            # Renvoie une erreur 400 si ces champs sont manquants
            return {"message": "Les champs 'title' et 'assigned_to' sont obligatoires."}, 400

        # Vérifie que l'utilisateur n'est pas admin ET qu'il ne crée une tâche que pour lui-même
        if current_user.role != "admin" and assigned_to_id != current_user.id:
            # Si ce n'est pas le cas, accès refusé (403)
            return {"message": "Vous ne pouvez créer une tâche que pour vous-même."}, 403

        # Recherche l'utilisateur à qui la tâche est assignée
        assigned_user = User.query.get(assigned_to_id)
        # Si cet utilisateur n'existe pas, renvoie une erreur 404
        if not assigned_user:
            return {"message": "Utilisateur assigné non trouvé."}, 404

        # Récupère l'ID du projet si fourni
        project_id = data.get('project_id')
        if project_id:
            # Recherche le projet en base
            project = Project.query.get(project_id)
            # Si le projet n'existe pas, renvoie une erreur 404
            if not project:
                return {"message": "Projet non trouvé."}, 404

        # Récupère la description, le statut, la priorité depuis les données reçues
        description = data.get('description')
        status = data.get('status', 'pending')  # statut par défaut 'pending'
        priority = data.get('priority', 'medium')  # priorité par défaut 'medium'

        # Récupère la date d'échéance sous forme de chaîne
        due_date_str = data.get('due_date')
        due_date = None
        if due_date_str:
            try:
                # Tente de convertir la chaîne ISO en objet datetime
                due_date = datetime.fromisoformat(due_date_str)
            except ValueError:
                # Si format invalide, renvoie une erreur 400
                return {"message": "Format date invalide (AAAA-MM-JJ)."}, 400

        # Crée un nouvel objet Task avec les données reçues
        new_task = Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            assigned_to=assigned_to_id,
            project_id=project_id
        )

        # Récupère la liste des noms de tags
        tags_names = data.get('tags', [])
        # Pour chaque nom de tag
        for tag_name in tags_names:
            # Cherche si le tag existe déjà en base
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                # Si oui, l'ajoute à la liste des tags de la tâche
                new_task.tags.append(tag)
            else:
                # Sinon, crée un nouveau tag et l'ajoute en base et à la tâche
                new_tag = Tag(name=tag_name)
                db.session.add(new_tag)
                new_task.tags.append(new_tag)

        # Ajoute la nouvelle tâche à la session de base de données
        db.session.add(new_task)
        # Sauvegarde toutes les modifications (INSERT en base)
        db.session.commit()

        # Renvoie un message de succès avec l'ID de la tâche créée et un code 201
        return {"message": "Tâche créée", "task_id": new_task.id}, 201

    except Exception as e:
        # En cas d'erreur, affiche l'erreur dans la console
        print("Erreur création tâche :", e)
        # Renvoie un message générique d'erreur serveur
        return {"message": "Erreur serveur"}, 500


# Fonction protégée par JWT pour récupérer les tâches selon rôle
@jwt_required()
def get_tasks():
    try:
        # Récupère l'UID de l'utilisateur courant
        current_uid = get_jwt_identity()
        # Recherche l'utilisateur en base
        current_user = User.query.filter_by(uid=current_uid).first()

        # Si l'utilisateur est admin, récupère toutes les tâches
        if current_user.role == "admin":
            tasks = Task.query.all()
        else:
            # Sinon, récupère seulement les tâches assignées à l'utilisateur
            tasks = Task.query.filter_by(assigned_to=current_user.id).all()

        # Liste pour stocker le résultat à retourner
        results = []
        # Parcourt toutes les tâches récupérées
        for t in tasks:
            # Construit un dictionnaire avec les infos utiles de la tâche
            results.append({
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "priority": t.priority,
                # Convertit la date en chaîne ISO si présente
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "assigned_to": t.assigned_to,
                "project_id": t.project_id,
                # Liste des noms des tags liés à la tâche
                "tags": [tag.name for tag in t.tags]
            })

        # Renvoie la liste des tâches avec code 200 OK
        return results, 200

    except Exception as e:
        # Affiche l'erreur en console
        print("Erreur:", e)
        # Renvoie une erreur serveur 500
        return {"message": "Erreur serveur"}, 500


# Fonction protégée par JWT pour récupérer une tâche précise via son ID
@jwt_required()
def get_task(task_id):
    try:
        # Recherche la tâche par son ID
        task = Task.query.get(task_id)
        # Si la tâche n'existe pas, renvoie erreur 404
        if not task:
            return {"message": "Tâche non trouvée"}, 404

        # Récupère l'UID utilisateur courant
        current_uid = get_jwt_identity()
        # Recherche l'utilisateur en base
        current_user = User.query.filter_by(uid=current_uid).first()

        # Si l'utilisateur n'est pas admin et n'est pas assigné à la tâche => accès refusé
        if current_user.role != "admin" and task.assigned_to != current_user.id:
            return {"message": "Accès refusé"}, 403

        # Prépare les données de la tâche à renvoyer
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

        # Renvoie les données avec code 200 OK
        return result, 200

    except Exception as e:
        # Affiche l'erreur en console
        print("Erreur:", e)
        # Renvoie une erreur serveur 500
        return {"message": "Erreur serveur"}, 500


# Fonction protégée par JWT pour mettre à jour une tâche existante
@jwt_required()
def update_task(task_id):
    try:
        # Recherche la tâche par son ID
        task = Task.query.get(task_id)
        # Si tâche non trouvée, erreur 404
        if not task:
            return {"message": "Tâche non trouvée"}, 404

        # Récupère l'UID utilisateur courant
        current_uid = get_jwt_identity()
        # Recherche l'utilisateur en base
        current_user = User.query.filter_by(uid=current_uid).first()

        # Vérifie que l'utilisateur est admin ou assigné à la tâche, sinon accès refusé
        if current_user.role != "admin" and task.assigned_to != current_user.id:
            return {"message": "Accès refusé"}, 403

        # Récupère les données JSON envoyées
        data = request.get_json()

        # Met à jour chaque champ si présent dans les données, sinon garde la valeur actuelle
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.status = data.get('status', task.status)
        task.priority = data.get('priority', task.priority)

        # Mise à jour de la date d'échéance si fournie
        due_date_str = data.get('due_date')
        if due_date_str:
            try:
                task.due_date = datetime.fromisoformat(due_date_str)
            except ValueError:
                # En cas de date invalide, erreur 400
                return {"message": "Date invalide"}, 400

        # Mise à jour du projet si fourni
        project_id = data.get('project_id')
        if project_id:
            # Vérifie que le projet existe
            project = Project.query.get(project_id)
            if not project:
                return {"message": "Projet non trouvé"}, 404
            # Met à jour l'id du projet lié à la tâche
            task.project_id = project_id

        # Mise à jour de l'utilisateur assigné si fourni
        assigned_to_id = data.get('assigned_to')
        if assigned_to_id:
            # Si l'utilisateur n'est pas admin, il ne peut réassigner qu'à lui-même
            if current_user.role != "admin" and assigned_to_id != current_user.id:
                return {"message": "Vous ne pouvez réassigner cette tâche qu'à vous-même."}, 403
            # Vérifie que l'utilisateur assigné existe
            user = User.query.get(assigned_to_id)
            if not user:
                return {"message": "Utilisateur assigné non trouvé"}, 404
            # Met à jour l'assignation
            task.assigned_to = assigned_to_id

        # Mise à jour des tags si fournis (liste)
        tags_names = data.get('tags')
        if tags_names is not None:
            # Vide la liste actuelle de tags
            task.tags.clear()
            # Pour chaque nom de tag
            for name in tags_names:
                # Cherche le tag en base
                tag = Tag.query.filter_by(name=name).first()
                if tag:
                    # Ajoute le tag existant
                    task.tags.append(tag)
                else:
                    # Sinon crée un nouveau tag et l'ajoute
                    new_tag = Tag(name=name)
                    db.session.add(new_tag)
                    task.tags.append(new_tag)

        # Enregistre les changements en base
        db.session.commit()
        # Renvoie message succès
        return {"message": "Tâche mise à jour"}, 200

    except Exception as e:
        # Affiche l'erreur en console
        print("Erreur:", e)
        # Renvoie erreur serveur 500
        return {"message": "Erreur serveur"}, 500


# Fonction protégée par JWT pour supprimer une tâche
@jwt_required()
def delete_task(task_id):
    try:
        # Recherche la tâche par son ID
        task = Task.query.get(task_id)
        # Si tâche non trouvée, erreur 404
        if not task:
            return {"message": "Tâche non trouvée"}, 404

        # Récupère l'UID utilisateur courant
        current_uid = get_jwt_identity()
        # Recherche l'utilisateur en base
        current_user = User.query.filter_by(uid=current_uid).first()

        # Seuls les admins peuvent supprimer une tâche
        if current_user.role != "admin":
            return {"message": "Seuls les administrateurs peuvent supprimer une tâche."}, 403

        # Supprime la tâche de la session
        db.session.delete(task)
        # Enregistre la suppression en base
        db.session.commit()

        # Renvoie message succès
        return {"message": "Tâche supprimée"}, 200

    except Exception as e:
        # Affiche l'erreur en console
        print("Erreur:", e)
        # Renvoie erreur serveur 500
        return {"message": "Erreur serveur"}, 500
