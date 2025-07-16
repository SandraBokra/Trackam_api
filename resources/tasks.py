from flask_restful import Resource
from helpers.tasks import *

class TaskApi(Resource):

    @jwt_required()
    def get(self, route, task_id=None):
        if route == "all":
            return get_tasks()
        elif route == "one" and task_id:
            return get_task(task_id)
        else:
            return {"message": f"Route GET inconnue ou ID manquant : {route}"}, 400

    @jwt_required()
    def post(self, route, task_id=None):
        if route == "create":
            return create_task()
        else:
            return {"message": f"Route POST inconnue : {route}"}, 400

    @jwt_required()
    def put(self, route, task_id=None):
        if route == "update" and task_id:
            return update_task(task_id)
        else:
            return {"message": f"Route PUT inconnue ou ID manquant : {route}"}, 400

    @jwt_required()
    def delete(self, route, task_id=None):
        if route == "delete" and task_id:
            return delete_task(task_id)
        else:
            return {"message": f"Route DELETE inconnue ou ID manquant : {route}"}, 400

