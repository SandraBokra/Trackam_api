from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from config.constant import DATABASE_URI  
from config.db import db


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

api = Api(app)


with app.app_context():
    db.create_all()


if __name__=="__main__":
    app.run(debug=True)