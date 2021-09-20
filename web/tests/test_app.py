import unittest
import os
import json

import pytest
from pymongo import MongoClient
from src import create_app
import bcrypt

class TestImgClassificationAuthApp(unittest.TestCase):

    def setUp(self):
        """set up app with testo params"""
        app = create_app({
                'TESTING': True,
                'DATABASE': 'test_db',
                'DB_HOST': "mongodb://db:27017"
                })
        self.client = app.test_client()

        client = MongoClient("mongodb://db:27017")
        self.db = client['test_db']

    def tearDown(self):
        """
        Drop the test database
        """
        client = MongoClient("mongodb://db:27017")
        client.drop_database("test_db")

    def test_home(self):
        "Check home page working"
        response = self.client.get("/")
        assert response.status_code == 200

    def test_register_new_user(self):
        "Test new user registration is ok"
        username = 'test_user'
        password = 'password'

        data = json.dumps({
            'username': username,
            'password': password
            }
        )

        response = self.client.post(
                            "/register",
                            headers={"Content-Type": "application/json"},
                            data=data,
                            follow_redirects=True
                            )
        data = response.get_json()
        "check status is ok"
        assert data['status'] == 200
        "check user exist and password has been hashed"
        user = self.db.Users.find_one({"Username": username})
        assert user['Username'] == username
        hashed_pwd = bcrypt.hashpw(password.encode('utf8'),user['Password'])
        assert hashed_pwd == user['Password']

    def test_register_existing_user(self):
        """
        Test if status code correct when try to register an existing user
        """
        username = 'test_user'
        password = 'password'
        tokens = 10
        # create a user in the db
        user = self.db.Users.insert_one({
                "Username": username,
                "Password": password,
                "Admin": 0,
                "Tokens":10
                        })
        # call register with same data
        data = json.dumps({
            'username': username,
            'password': password
            }
        )
        response = self.client.post(
                            "/register",
                            headers={"Content-Type": "application/json"},
                            data=data,
                            follow_redirects=True
                            )
        data = response.get_json()
        assert data['status'] == 301

    def test_refill_with_admin(self):
        """
        Test if refill works
        """
        # create admin user
        username = "Admin_User"
        password = "Admin_User_PWD"
        hashed_pwd = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        self.db.Users.insert_one({
                "Username": username,
                "Password": hashed_pwd,
                "Admin": 1,
                "Tokens":10
                        })
        # create user to refill
        user_to_refill = "test_user"
        user_pwd = "test_pwd" # no need to hash
        self.db.Users.insert_one({
                "Username": user_to_refill,
                "Password": user_pwd,
                "Admin": 0,
                "Tokens":10
                        })

        # test if refill works
        data = json.dumps({
            "username": username,
            "password": password,
            "user_to_refill": user_to_refill,
            "amount": 10
        })
        response = self.client.post(
                    "/refill",
                    headers={"Content-Type": "application/json"},
                    data=data,
                    follow_redirects=True
                    )
        res = response.get_json()
        assert response.status_code == 200
        assert res['status'] == 200
        user = self.db.Users.find_one({"Username": user_to_refill})
        assert user['Tokens'] == 20

    def test_refill_wrong_no_admin(self):
        """
        Test if call refill with wrong admin details
        """
        username = "Admin_User"
        password = "Admin_User_PWD"
        user_to_refill = "test_user"
        amount = 10
        data = json.dumps({
            "username": username,
            "password": password,
            "user_to_refill": user_to_refill,
            "amount": amount
        })
        response = self.client.post(
                    "/refill",
                    headers={"Content-Type": "application/json"},
                    data=data,
                    follow_redirects=True
                    )
        res = response.get_json()

        assert res['status'] == 304
