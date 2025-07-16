from models.trackam import User
from config.db import db
import bcrypt
from datetime import timedelta
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity
import re
from flask import request, jsonify


# Tentatives en mémoire (dictionnaire simple, mieux avec Redis pour la prod)
login_attempts = {}

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(stored_password: str, input_password: str) -> bool:
    if isinstance(stored_password, str):
        stored_password = stored_password.encode('utf-8')
    return bcrypt.checkpw(input_password.encode('utf-8'), stored_password)

def is_password_strong(password: str) -> bool:
    """Force minimale : 8 caractères, majuscule, minuscule, chiffre, caractère spécial"""
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )

def create_user():
    try:
        data = request.get_json()
        print("Reçu:", data)

        full_name = data.get("full_name")
        email = data.get("email")
        password = data.get("password")

        if not full_name or not email or not password:
            return {"message": "Tous les champs sont requis"}, 400

        if not is_password_strong(password):
            return {"message": "Le mot de passe est trop faible. Il doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial."}, 400

        if User.query.filter_by(email=email).first():
            return {"message": "Cet email est déjà utilisé"}, 409

        hashed_password = hash_password(password)

        new_user = User(
            full_name=full_name,
            email=email,
            password=hashed_password.decode('utf-8'),
            role="member",
                # email_verified=False  # Ajouté
        )

        db.session.add(new_user)
        db.session.commit()

        return {"message": "Inscription réussie"}, 201

    except Exception as e:
        print("Erreur serveur:", str(e))
        return {"message": "Erreur serveur : " + str(e)}, 500

def login_user():
    try:
        full_name = request.json.get('full_name')
        password = request.json.get('password')

        if not full_name or not password:
            return {"statut": "erreur", "message": "Nom d'utilisateur et mot de passe requis"}, 400

        # Vérifie les tentatives précédentes
        attempts = login_attempts.get(full_name, 0)
        if attempts >= 5:
            return {"statut": "erreur", "message": "Trop de tentatives échouées. Réessaye plus tard."}, 403

        login_user = User.query.filter_by(full_name=full_name).first()

        if login_user and verify_password(login_user.password, password):
            # Réinitialise les tentatives si succès
            login_attempts[full_name] = 0

            expires = timedelta(hours=1)
            access_token = create_access_token(identity=login_user.u_uid, expires_delta=expires)

            rs = {
                "u_uid": login_user.u_uid,
                "username": login_user.username,
                "email": login_user.email,
                "role": login_user.role,
                "date_inscription": login_user.date_inscription.isoformat(),  # Converti proprement
                "email_verified": login_user.email_verified
            }

            return {
                "statut": "succes",
                "access_token": access_token,
                "infos_user": rs
            }, 200

        else:
            login_attempts[full_name] = attempts + 1
            return {"statut": "erreur", "message": "Nom d'utilisateur ou mot de passe invalide"}, 401

    except Exception as e:
        return {"message": f"Erreur serveur : {str(e)}"}, 500

def create_admin():
    try:
        existing_admin = User.query.filter_by(role='admin').first()

        if not existing_admin:
            admin_password = hash_password('admin123')
            admin = User(
                username='admin',
                email='admin@example.com',
                password=admin_password.decode('utf-8'),
                role='admin',
                email_verified=True  # On considère que l’admin est validé
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin créé avec succès")
        else:
            print("Admin déjà existant")
    except Exception as e:
        print("Erreur lors de la création de l'admin :", str(e))


# admin_bp = Blueprint('admin_bp', _name_)  # Tu peux l’appeler comme tu veux

# @admin_bp.route("/utilisateurs/role", methods=["PUT"])
# @jwt_required()
# def update_user_role():
#     try:
#         current_uid = get_jwt_identity()
#         current_user = User.query.filter_by(u_uid=current_uid).first()

#         if not current_user or current_user.role != "admin":
#             return jsonify({"message": "Accès refusé. Seul un admin peut modifier les rôles."}), 403

#         data = request.get_json()
#         target_email = data.get("email")
#         new_role = data.get("role")

#         if new_role not in ["utilisateur", "manager", "admin"]:
#             return jsonify({"message": "Rôle invalide"}), 400

#         user_to_update = User.query.filter_by(email=target_email).first()

#         if not user_to_update:
#             return jsonify({"message": "Utilisateur non trouvé"}), 404

#         user_to_update.role = new_role
#         db.session.commit()

#         return jsonify({"message": f"Rôle mis à jour pour {user_to_update.username} en {new_role}"}), 200

#     except Exception as e:
#         return jsonify({"message": f"Erreur serveur : {str(e)}"}), 500
# [12:57, 16/07/2025] +225 59 40 25 20: from flask_restful import Resource
# from helpers.users import *

# class UserAPI(Resource):
#     def post(self, route):
        
#         if route == "create":
#             return CreateUser()
        
#         if route == "login":
#             return LoginUser()
    
#     # def get(self, route):
#     #     if route == "me":
#     #         return GetCurrentUser()