from flask_restful import Resource
from helpers.tasks import *

class TaskApi(Resource):

    def post(self, route, task_id=None):
        if route == "create":
            return create_task()
        else:
            return {"message": f"Route POST inconnue : {route}"}, 400

    def get(self, route, task_id=None):
        if route == "all":
            return get_tasks()
        elif route == "one":
            if task_id is None:
                return {"message": "task_id est requis pour 'one'"}, 400
            return get_task(task_id)
        else:
            return {"message": f"Route GET inconnue : {route}"}, 400

    def put(self, route, task_id=None):
        if route == "update":
            if task_id is None:
                return {"message": "task_id est requis pour 'update'"}, 400
            return update_task(task_id)
        else:
            return {"message": f"Route PUT inconnue : {route}"}, 400

    def delete(self, route, task_id=None):
        if route == "delete":
            if task_id is None:
                return {"message": "task_id est requis pour 'delete'"}, 400
            return delete_task(task_id)
        else:
            return {"message": f"Route DELETE inconnue : {route}"}, 400



