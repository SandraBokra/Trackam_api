from models.trackam import User
from config.db import db
import bcrypt
from datetime import timedelta
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity
import re
from flask import request, jsonify

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

def create_admin():
    try:
        existing_admin = User.query.filter_by(role='admin').first()

        if not existing_admin:
            admin_password = hash_password('admin123')
            admin = User(
                full_name='admin',
                email='admin@example.com',
                password=admin_password.decode('utf-8'),
                role='admin',
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin créé avec succès")
        else:
            print("Admin déjà existant")
    except Exception as e:
        print("Erreur lors de la création de l'admin :", str(e))



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