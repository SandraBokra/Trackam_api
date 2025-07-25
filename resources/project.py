from flask_restful import Resource
from helpers.project import *


class ProjectApi(Resource):

    def post(self, route):
        if route == "create_project":
            return CreateProject()

        if route == "get_single_project":
            return GetSingleProject()
        
        if route == "update_project":
            return UpdateProject()
    
        if route == "delete_project":
            return DeleteProject()
        
        if route == "get_all_projects_by_user":
            return GetAllProjectsByUserId()

    
    def get(self, route):
        if route == "get_all_projects":
            return GetAllProjects()
        


