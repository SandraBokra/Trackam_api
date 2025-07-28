from datetime import timedelta
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config.constant import DATABASE_URI
from config.db import db
from resources.comment_task import CommentApi
from resources.project import ProjectApi
from resources.tag import TagApi
from resources.tasks import TaskApi
from resources.user import UserApi


app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

db.init_app(app)
jwt = JWTManager(app)
api = Api(app)
migrate= Migrate(app, db)

api.add_resource(UserApi, '/api/auth/<string:route>', endpoint='all_auth', methods=['GET', 'POST', 'DELETE', 'PATCH'])
api.add_resource(TaskApi, '/api/tasks/<string:route>', endpoint='all_tasks', methods=['GET', 'POST', 'DELETE', 'PATCH'])
api.add_resource(ProjectApi, '/api/projects/<string:route>', endpoint='all_projects', methods=['GET', 'POST', 'DELETE', 'PATCH'])
api.add_resource(CommentApi, '/api/comments/<string:route>', endpoint='all_comments', methods=['GET', 'POST', 'DELETE', 'PATCH'])
api.add_resource(TagApi, '/api/tags/<string:route>', endpoint='all_tags', methods=['GET', 'POST', 'DELETE', 'PATCH'])

with app.app_context():
    db.create_all()


if __name__=="__main__":
    app.run(debug=True)