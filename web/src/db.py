from flask import current_app, g
from pymongo import MongoClient

def get_db():
    if 'db' not in g:
        client = MongoClient(current_app.config['DB_HOST'])
        g.db = client[current_app.config['DATABASE']]
    return g.db
