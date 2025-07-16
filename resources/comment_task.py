from flask_restful import Resource
from helpers.comment_task import *

class CommentApi(Resource):

    def post(self, route, comment_id=None):
        if route == "CreateComment":
            return create_comment()
        else:
            return {"message": f"Route POST inconnue : {route}"}, 400

    def get(self, route, comment_id=None):
        if route == "AllComment":
            return get_comments()
        elif route == "OneComment":
            if comment_id is None:
                return {"message": "comment_id est requis pour 'one'"}, 400
            return get_comment(comment_id)
        else:
            return {"message": f"Route GET inconnue : {route}"}, 400

    def put(self, route, comment_id=None):
        if route == "UpdateComment":
            if comment_id is None:
                return {"message": "comment_id est requis pour 'update'"}, 400
            return update_comment(comment_id)
        else:
            return {"message": f"Route PUT inconnue : {route}"}, 400

    def delete(self, route, comment_id=None):
        if route == "DeleteComment":
            if comment_id is None:
                return {"message": "comment_id est requis pour 'delete'"}, 400
            return delete_comment(comment_id)
        else:
            return {"message": f"Route DELETE inconnue : {route}"}, 400
