from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from helpers.tasks import *
from helpers.user import create_admin
from flask_jwt_extended import JWTManager

from config.constant import DATABASE_URI
from config.db import db
from resources.tasks import TaskApi
from resources.user import UserApi


app = Flask(__name__)
CORS(app)

# ✅ Configuration obligatoire
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Met une vraie clé en prod

# ✅ Initialisation du JWT
jwt = JWTManager(app)


app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

api = Api(app)

migrate= Migrate(app, db)

api.add_resource(TaskApi, '/tasks/<string:route>')


api.add_resource(UserApi, '/auth/<string:route>')


with app.app_context():
    db.create_all()
    create_admin()


if __name__=="__main__":
    app.run(debug=True)