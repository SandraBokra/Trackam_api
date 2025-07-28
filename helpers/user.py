from models.trackam import User
from config.db import db
import bcrypt
from flask import request




def CreateUser():
    reponse = {}
    try:
        full_name = request.json.get('full_name')
        email = request.json.get('email')
        role = request.json.get('role')
        password = request.json.get('password')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        new_user = User()
        new_user.full_name = full_name
        new_user.email = email
        new_user.role = role
        new_user.password = hashed_password

        db.session.add(new_user)
        db.session.commit()


        reponse['status'] = 'success'


    except Exception as e:
        reponse['error_description'] = str(e)
        reponse['status'] = 'error'

    return reponse


def GetAllMember():
    reponse = {}
    try:
        users = User.query.all()
        result = []

        for user in users:
            if user.role == "member":
                result.append({
                    'id': user.uid,
                    'full_name': user.full_name,
                    'email': user.email,
                    'role': user.role,
                })

        reponse['status'] = 'success'
        reponse['result'] = result

    except Exception as e:
        reponse['error_description'] = str(e)
        reponse['status'] = 'error'

    return reponse


def GetAllAdmin():
    reponse = {}
    try:
        users = User.query.all()
        result = []

        for user in users:
            if user.role == "admin":
                result.append({
                    'id': user.uid,
                    'full_name': user.full_name,
                    'email': user.email,
                    'role': user.role
                })

        reponse['status'] = 'success'
        reponse['result'] = result

    except Exception as e:
        reponse['error_description'] = str(e)
        reponse['status'] = 'error'

    return reponse

def GetSingleMember():
    reponse = {}
    try:
        uid = request.json.get('uid')
        single_user = User.query.filter_by(uid=uid).first()

        if single_user is None:
            reponse['status'] = 'error'
            reponse['message'] = 'Utilisateur introuvable'

        if single_user.role == "member":
            result = {
                'uid': single_user.uid,
                'full_name': single_user.full_name,
                'email': single_user.email,
                'role': single_user.role,            
                'created_at': str(single_user.created_at)
            }
            reponse['status'] = 'success'
            reponse['result'] = result
        else:
            reponse['status'] = 'error'
            reponse['message'] = 'Utilisateur introuvable'

    except Exception as e:
        reponse['error_description'] = str(e)
        reponse['status'] = 'error'

    return reponse


def GetSingleAdmin():
    reponse = {}
    try:
        uid = request.json.get('uid')
        single_user = User.query.filter_by(uid=uid).first()

        if single_user is None:
            reponse['status'] = 'error'
            reponse['message'] = 'Utilisateur introuvable'

        if single_user.role == "admin":
            result = {
                'uid': single_user.uid,
                'full_name': single_user.full_name,
                'email': single_user.email,
                'role': single_user.role,            
                'created_at': str(single_user.created_at)
            }
            reponse['status'] = 'success'
            reponse['result'] = result
        else:
            reponse['status'] = 'error'
            reponse['message'] = 'Utilisateur introuvable'

    except Exception as e:
        reponse['error_description'] = str(e)
        reponse['status'] = 'error'

    return reponse

    
def UpdateUser():
    reponse = {}
    try:
        # Debug: Afficher toutes les données reçues
        print("Données reçues dans UpdateUser:", request.json)
        
        uid = request.json.get('uid')
        full_name = request.json.get('full_name')
        old_password = request.json.get('old_password')
        new_password = request.json.get('new_password')

        print(f"UID: {uid}, Full Name: {full_name}")
        print(f"Old Password présent: {bool(old_password)}, New Password présent: {bool(new_password)}")

        user = User.query.filter_by(uid=uid).first()
        
        if not user:
            print(f"Utilisateur non trouvé pour l'UID: {uid}")
            reponse['status'] = 'error'
            reponse['message'] = 'Utilisateur introuvable'
            return reponse

        print(f"Utilisateur trouvé: {user.full_name} ({user.email})")

        # Vérification de l'ancien mot de passe si nouveau mot de passe demandé
        if new_password:
            if not old_password:
                print("Ancien mot de passe manquant")
                reponse['status'] = 'error'
                reponse['message'] = "L'ancien mot de passe est requis pour changer le mot de passe"
                return reponse

            if not bcrypt.checkpw(old_password.encode('utf-8'), user.password.encode('utf-8')):
                print("Ancien mot de passe incorrect")
                reponse['status'] = 'error'
                reponse['message'] = "Ancien mot de passe incorrect"
                return reponse

            hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            user.password = hashed_new_password
            print("Mot de passe mis à jour")

        # Mise à jour uniquement du nom complet
        if full_name:
            old_name = user.full_name
            user.full_name = full_name
            print(f"Nom mis à jour: {old_name} -> {full_name}")

        # Sauvegarder les changements
        db.session.commit()
        print("Changements sauvegardés en base de données")

        reponse['status'] = 'success'
        reponse['message'] = 'Profil mis à jour avec succès'

    except Exception as e:
        print(f"Erreur dans UpdateUser: {str(e)}")
        db.session.rollback()  # Rollback en cas d'erreur
        reponse['status'] = 'error'
        reponse['error_description'] = str(e)

    return reponse



def GetUserProfile():
    reponse = {}
    try:
        uid = request.json.get('uid')
        user = User.query.filter_by(uid=uid).first()

        if not user:
            reponse['status'] = 'error'
            reponse['message'] = 'Utilisateur introuvable'
            return reponse

        result = {
            'uid': user.uid,
            'full_name': user.full_name,
            'email': user.email,
            'role': user.role,
            'created_at': str(user.created_at)
        }

        reponse['status'] = 'success'
        reponse['result'] = result
    except Exception as e:
        reponse['status'] = 'error'
        reponse['error_description'] = str(e)

    return reponse


def DeleteUser():
    reponse = {}
    try:
        uid = request.json.get('uid')
        user = User.query.filter_by(uid=uid).first()

        if not user:
            reponse['status'] = 'error'
            reponse['message'] = 'Utilisateur introuvable'

        db.session.delete(user)
        db.session.commit()

        reponse['status'] = 'success'
        reponse['message'] = 'Utilisateur supprimé avec succès'

    except Exception as e:
        reponse['error_description'] = str(e)
        reponse['status'] = 'error'

    return reponse