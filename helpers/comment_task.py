from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.trackam import db, Comment, User, Task
import datetime

# Créer un commentaire
@jwt_required()
def create_comment():
    try:
        data = request.get_json()
        content = data.get('content')
        task_id = data.get('task_id')  # ici task_id = uid (string)

        if not content or not task_id:
            return {"message": "Les champs 'content' et 'task_id' sont obligatoires."}, 400

        # Cherche la tâche par uid (string), PAS par id (int)
        task = Task.query.filter_by(uid=task_id).first()
        if not task:
            return {"message": "Tâche non trouvée."}, 404

        # Récupère l'utilisateur connecté via email dans le token
        current_email = get_jwt_identity()
        user = User.query.filter_by(email=current_email).first()
        if not user:
            return {"message": "Utilisateur non authentifié."}, 401

        # Vérifie que la tâche lui est assignée (assigned_to est uid string)
        if task.assigned_to != user.uid:
            return {"message": "Vous ne pouvez commenter que les tâches qui vous sont assignées."}, 403

        # Création du commentaire (user_id est uid string)
        new_comment = Comment(
            content=content,
            task_id=task.uid,  # bien mettre uid (string)
            user_id=user.uid
        )
        db.session.add(new_comment)
        db.session.commit()

        return {"message": "Commentaire ajouté", "comment_id": new_comment.id}, 201

    except Exception as e:
        print("Erreur création commentaire :", e)
        return {"message": "Erreur serveur"}, 500


# Lister tous les commentaires (admin ou utilisateur uniquement ses propres commentaires)
@jwt_required()
def get_comments():
    try:
        current_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_email).first()

        if current_user.role == "admin":
            comments = Comment.query.all()
        else:
            # user_id dans Comment est uid string, on filtre par user.uid
            comments = Comment.query.filter_by(user_id=current_user.uid).all()

        result = []
        for c in comments:
            result.append({
                "id": c.id,
                "content": c.content,
                "created_at": c.created_at.isoformat(),
                "task_id": c.task_id,
                "user_id": c.user_id
            })

        return result, 200

    except Exception as e:
        print("Erreur récupération commentaires :", e)
        return {"message": "Erreur serveur"}, 500


# Obtenir un commentaire par son ID
@jwt_required()
def get_comment(comment_id):
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return {"message": "Commentaire non trouvé."}, 404

        current_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_email).first()

        # Compare toujours avec uid string
        if comment.user_id != current_user.uid and current_user.role != "admin":
            return {"message": "Accès refusé."}, 403

        result = {
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at.isoformat(),
            "task_id": comment.task_id,
            "user_id": comment.user_id
        }

        return result, 200

    except Exception as e:
        print("Erreur récupération commentaire :", e)
        return {"message": "Erreur serveur"}, 500


# Modifier un commentaire (uniquement par l’auteur ou admin)
@jwt_required()
def update_comment(comment_id):
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return {"message": "Commentaire non trouvé."}, 404

        current_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_email).first()

        # Vérifie auteur ou admin via uid
        if comment.user_id != current_user.uid and current_user.role != "admin":
            return {"message": "Vous ne pouvez modifier que vos propres commentaires."}, 403

        # Si pas admin, la tâche doit être assignée à lui (uid)
        if current_user.role != "admin":
            task = Task.query.filter_by(uid=comment.task_id).first()
            if not task or task.assigned_to != current_user.uid:
                return {"message": "Vous ne pouvez modifier un commentaire que sur une tâche qui vous est assignée."}, 403

        data = request.get_json()
        content = data.get('content')

        if not content:
            return {"message": "Le champ 'content' est obligatoire."}, 400

        comment.content = content
        db.session.commit()

        return {"message": "Commentaire mis à jour."}, 200

    except Exception as e:
        print("Erreur modification commentaire :", e)
        return {"message": "Erreur serveur"}, 500


# Supprimer un commentaire (seulement admin ou auteur)
@jwt_required()
def delete_comment(comment_id):
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return {"message": "Commentaire non trouvé."}, 404

        current_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_email).first()

        # Si pas admin, vérifier que c’est auteur ET tâche assignée à lui
        if current_user.role != "admin":
            if comment.user_id != current_user.uid:
                return {"message": "Seul l’auteur ou un admin peut supprimer ce commentaire."}, 403

            task = Task.query.filter_by(uid=comment.task_id).first()
            if not task or task.assigned_to != current_user.uid:
                return {"message": "Vous ne pouvez supprimer un commentaire que sur une tâche qui vous est assignée."}, 403

        db.session.delete(comment)
        db.session.commit()

        return {"message": "Commentaire supprimé."}, 200

    except Exception as e:
        print("Erreur suppression commentaire :", e)
        return {"message": "Erreur serveur"}, 500
