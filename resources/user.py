from flask_restful import Resource
from helpers.auth import *
from helpers.admin import create_user

class UserApi(Resource):
    
    def post(self, route):
        if route == "register":
            return create_user()

        if route == "login":
            return login_user()
        else:
            return {"message": f"Route POST inconnue : {route}"}, 400