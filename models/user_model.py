from datetime import datetime
from flask import Flask
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from db import mongo
from brain2 import app


class User:
    def __init__(self, first_name, last_name, email, password, birthdate, family_id, client, consultant, manager, administrator):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.birthdate = birthdate
        self.family_id = family_id
        self.client = True
        self.consultant  = False
        self.manager = False
        self.administrator = False
        self.created_at = datetime.now()
        self.last_login = None

    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one({"email": email})

    def save(self):
        mongo.db.users.insert_one(self.__dict__)

    def update_last_login(self):
        self.last_login = datetime.now()

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
