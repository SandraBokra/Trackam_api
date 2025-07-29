from models.trackam import User
import bcrypt
from flask_jwt_extended import create_access_token
from flask import jsonify, request



def LoginUser():
    try:
        email = request.json.get('email')
        password = request.json.get('password')

        login_user = User.query.filter_by(email=email).first()

        if login_user and bcrypt.checkpw(password.encode('utf-8'), login_user.password.encode('utf-8')):
            access_token = create_access_token(identity=email)

            rs = {
                'uid': login_user.uid,
                'full_name': login_user.full_name,
                'email': login_user.email,
                'role': login_user.role,
                'created_at': str(login_user.created_at)
            }

            return {
                'status': 'success',
                'message': 'Login successful',
                'role': login_user.role,
                'uid': login_user.uid,
                'user_infos': rs,
                'access_token': access_token
            }, 200

        return {
            'status': 'error',
            'message': 'Invalid username or password'
        }, 401

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }, 500

