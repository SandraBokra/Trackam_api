from models.trackam import User
import bcrypt
from flask_jwt_extended import create_access_token
from flask import request



def LoginUser():
    reponse = {}

    try:
        email = request.json.get('email')
        password = request.json.get('password')

        login_user = User.query.filter_by(email=email).first()

        if login_user and bcrypt.checkpw(password.encode('utf-8'), login_user.password.encode('utf-8')):
            
            access_token = create_access_token(identity=email)

            rs = {}
            rs['uid'] = login_user.uid
            rs['full_name'] = login_user.full_name
            rs['email'] = login_user.email
            rs['role'] = login_user.role
            rs['created_at'] = str(login_user.created_at)
            rs['password'] = login_user.password

            reponse['status'] = 'success'
            reponse['message'] = 'Login successful'
            reponse['user_infos'] = rs
            reponse['access_token'] = access_token

        else:
            reponse['status'] = 'error'
            reponse['message'] = 'Invalid username or password'

    except Exception as e:
        reponse['status'] = 'error'
        reponse['message'] = str(e)

    return reponse 
