from flask_restful import Resource
from helpers.project import *


class ProjectApi(Resource):

    def post(self, route):
        if route == "create_project":
            return create_project()
        else:
            return {"message": f"Route POST inconnue : {route}"}, 400

    def get(self, route):
        if route == "readAll_projects":
            return get_all_projects()
        elif route == "readOne_project":
            return get_project()
        else:
            return {"message": f"Route GET inconnue : {route}"}, 400

    def put(self, route):
        if route == "update_project":
            return update_project()
        else:
            return {"message": f"Route PUT inconnue : {route}"}, 400

    def delete(self, route):
        if route == "delete_project":
            return delete_project()
        else:
            return {"message": f"Route DELETE inconnue : {route}"}, 400
