from flask_restful import Resource
from helpers.tag import *


class TagApi(Resource):

    def post(self, route):
        if route == "create_tag":
            return create_tag()
        else:
            return {"message": f"Route POST inconnue : {route}"}, 400
        
    def get(self, route):
        if route == "readAll_tags":
            return get_all_tags()
        elif route == "readOne_tag":
            return get_tag()
        else:
            return {"message": f"Route GET inconnue : {route}"}, 400

    def delete(self, route):
        if route == "delete_tag":
            return delete_tag()
        else:
            return {"message": f"Route DELETE inconnue : {route}"}, 400
    def put(self, route):
        if route == "update_tag":
            return update_tag()
        else:
            return {"message": f"Route PUT inconnue : {route}"}, 400
