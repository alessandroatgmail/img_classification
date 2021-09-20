import os
from flask import Flask,  jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt


def create_app(test_config=None):
    # create and cofigure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DB_HOST = "mongodb://db:27017",
        DATABASE="SimilarityDB"
    )
    api = Api(app)

    if test_config is None:
        # load the instance config, if it exists, when not in testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the config passed in
        app.config.from_mapping(test_config)

    class Home(Resource):
        def get(self):
            return "App online"
    # from .auth import Register
    from . import auth

    # register the Api
    api.add_resource(Home, "/")
    api.add_resource(auth.Register, "/register")
    api.add_resource(auth.Refill, "/refill")

    return app
