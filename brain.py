from flask import Flask, render_template, request, jsonify, redirect, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.collation import Collation
from flask_login import LoginManager, login_required, current_user
import json
from bson.json_util import dumps
from functools import wraps
import jwt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
import os
from flask_cors import CORS


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = "dsfdfasdfsdfsdfsdfsd"


jwt = JWTManager(app)
    


cors = CORS(app)


client = MongoClient(
    "mongodb+srv://desenvolvedor:desenvolvedor@financialapp.wwdb8xz.mongodb.net/?retryWrites=true&w=majority")

users = client.financialApp.users

@app.route('/')
def home():
    return{
        "message": "A home ainda não foi construída"
    }


@app.route('/login', methods=["POST"])
def login():
    email = request.json['email']
    password = request.json['password']

    user = users.find_one({
        "email": email
    })
    if check_password_hash(user['password'], password):
        access_token = create_access_token(identity=email)
        response = jsonify(access_token=access_token)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        return {
            "message": "password não confere"
        }


@app.route('/inserirUsuario', methods=["POST"])
def inserir_usuario():
    name = request.json['name']
    last_name  = request.json['last_name']
    birth_day = request.json['birth_day']
    email = request.json['email']
    password = request.json['password']
    family = request.json['family']


    users.insert_one({
        "name": name,
        "last_name": last_name,
        "birth_day": birth_day,
        "email": email,
        'family': family,
        "password": generate_password_hash(password),

    })
    return {
        "mensagem": "usuário inserido"
    }


@app.route('/protegida')
@jwt_required()
def protegida():
    msg = {
        "message":"Você chegou aqui"
    }
    return(msg)






if __name__ == "__main__":

    app.run(port=5000, debug=True)
