from flask_restful import Resource
from helpers.tasks import *


class TaskApi(Resource):

    def post(self, route):
        if route == "create":
            return create_task()
        else:
            return {"message": f"Route POST inconnue : {route}"}, 400

    def get(self, route):
        if route == "all":
            return get_tasks()
        elif route == "one":
            return get_task()
        else:
            return {"message": f"Route GET inconnue : {route}"}, 400

    def put(self, route):
        if route == "update":
            return update_task()
        else:
            return {"message": f"Route PUT inconnue : {route}"}, 400

    def delete(self, route):
        if route == "delete":
            return delete_task()
        else:
            return {"message": f"Route DELETE inconnue : {route}"}, 400
