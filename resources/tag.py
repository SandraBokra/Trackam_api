from flask_restful import Resource
from helpers.tag import *


class TagApi(Resource):

    def post(self, route):
        if route == "create_tag":
            return create_tag()
        else:
            return {"message": f"Route POST inconnue : {route}"}, 400