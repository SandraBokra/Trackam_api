from flask_restful import Resource
from helpers.tag import *


class TagApi(Resource):

    def post(self, route):
        if route == "create_tag":
            return CreateTag()
        
        if route == "get_single_tag":
            return GetSingleTag()

        if route == "delete_tag":
            return DeleteTag()
        
        if route == "update_tag":
            return UpdateTag()
       
        
    def get(self, route):
          if route == "get_all_tags":
            return GetAllTag()


