from flask_restful import Resource
from helpers.auth import *
from helpers.user import *

class UserApi(Resource):
    
    def post(self, route):
        if route == "create_user":
            return CreateUser()

        if route == "get_all_admin":
            return GetAllAdmin()

        if route == "get_single_member":
            return GetSingleMember()
        
        if route == "get_single_admin":
            return GetSingleAdmin()
        
        if route == "delete_user":
            return DeleteUser()
        
        if route == "login_user":
            return LoginUser()
        
        if route == "update_user":   # <-- ici
            return UpdateUser()
        if route == "get_user_profile":
            return GetUserProfile()

        
    def get(self, route):
        if route == "get_all_member":
            return GetAllMember()
        