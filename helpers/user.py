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
                    'id': user.id,
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


def GetAllAdmin():
    reponse = {}
    try:
        users = User.query.all()
        result = []

        for user in users:
            if user.role == "admin":
                result.append({
                    'id': user.id,
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