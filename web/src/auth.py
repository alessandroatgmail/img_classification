from flask import g, jsonify, request
from .db import get_db
from flask_restful import Resource
import bcrypt

def user_exist(username):
    db = get_db()
    user = db.Users.find_one({"Username":username})
    print ("user:{}".format(user))
    if user:
        return True
    else:
        return False

def check_admin(username, password):
    db = get_db()
    user = db.Users.find_one({"Username":username})
    if not user:
        return {"status": 304,
                "msg": "Admin user not exist"
                }
    hashed_pwd = bcrypt.hashpw(password.encode('utf8'), user['Password'])

    # if user["Password"] != hashed_pwd:
    #     return {
    #         "status": 304,
    #         "Invalid password for admin user"
    #         }

    return {"status": 200}

def count_tokens(username):
    db = get_db()
    user = db.Users.find_one({"Username":username})
    return user['Tokens']

class Register(Resource):
    """
    Register a new user
    """
    def post(self):
        db = get_db()
        postedData = request.get_json()
        username = postedData['username']
        password = postedData['password']

        if user_exist(username):
            retJson = {
                "status": 301,
                "msg": "User already registered"
            }
            return jsonify(retJson)
        hashed_pwd = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        db.Users.insert_one({"Username": username,
                            "Password": hashed_pwd,
                            "Admin": 0,
                            "Tokens": 10
                            })
        retJson = {
            "status": 200,
            "msg": "User registered"
        }

        return jsonify(retJson)

class Refill(Resource):
    """
    Refill tokens to user
    """
    def post(self):
        db = get_db()
        postedData = request.get_json()
        username = postedData['username']
        password = postedData['password']
        user_to_refill = postedData['user_to_refill']
        amount = postedData['amount']

        # check admin data
        retJson = check_admin(username, password)
        if retJson['status'] != 200:
            return jsonify(retJson)

        if not user_exist(user_to_refill):
            retJson = {"status": 301,
                        "msg": "user to refill does not exist"}

        current_tokens = count_tokens(user_to_refill)

        db.Users.update_one({
                "Username": user_to_refill
                }, {
                "$set": {"Tokens": current_tokens+amount }
                })

        retJson = {"status": 200,
                    "msg": "Amount refilled"}
        return jsonify(retJson)
