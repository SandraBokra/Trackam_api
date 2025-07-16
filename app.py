from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from helpers.admin import create_admin
from flask_jwt_extended import JWTManager
from config.constant import DATABASE_URI
from config.db import db
from resources.comment_task import CommentApi
from resources.project import ProjectApi
from resources.tasks import TaskApi
from resources.user import UserApi


app = Flask(__name__)
CORS(app)


app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
jwt = JWTManager(app)
api = Api(app)
migrate= Migrate(app, db)


api.add_resource(UserApi, '/auth/<string:route>', methods=["GET","POST","PATCH","DELETE"])
api.add_resource(TaskApi, '/tasks/<string:route>', '/tasks/<string:route>/<int:task_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
api.add_resource(ProjectApi, '/projects/<string:route>',  methods=['GET', 'POST','PUT', 'DELETE'])
api.add_resource(CommentApi, '/comments/<string:route>', '/comments/<string:route>/<int:comment_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])


with app.app_context():
    db.create_all()
    create_admin()


if __name__=="__main__":
    app.run(debug=True)