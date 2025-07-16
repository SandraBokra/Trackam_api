from models.trackam import User
from config.db import db
import bcrypt
from datetime import timedelta
from flask_jwt_extended import create_access_token
import re
from flask import request


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
            access_token = create_access_token(identity=login_user.uid, expires_delta=expires)

            rs = {
                "uid": login_user.uid,
                "full_name": login_user.full_name,
                "email": login_user.email,
                "role": login_user.role,
                "created_at": login_user.created_at.isoformat(),  # Converti proprement
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

