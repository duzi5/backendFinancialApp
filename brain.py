from flask import Flask, render_template, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.collation import Collation
from flask_login import LoginManager
import json
from bson.json_util import dumps

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)


client = MongoClient(
    "mongodb+srv://desenvolvedor:desenvolvedor@financialapp.wwdb8xz.mongodb.net/?retryWrites=true&w=majority")
users = client.financialApp.users


@app.route('/login', methods=["POST"])
def login():
    email = request.json['email']
    senha = request.json['senha']

    user = users.find_one({
        "email": email
    })
    if check_password_hash(user['senha'], senha):
        userinfos = json.loads(dumps(user))
        return userinfos['nome']
    else:
        return {
            "mensagem": "senha não confere"
        }


@app.route('/inserirUsuario', methods=["POST"])
def inserir_usuario():
    nome = request.json['nome']
    sobrenome = request.json['sobrenome']
    data_nascimento = request.json['data_nascimento']
    email = request.json['email']
    senha = request.json['senha']

    users.insert_one({
        "nome": nome,
        "sobrenome": sobrenome,
        "data_nascimento": data_nascimento,
        "email": email,
        "senha": generate_password_hash(senha)
    })
    return {
        "mensagem": "usuário inserido"
    }


if __name__ == "__main__":

    app.run(port=3000, debug=True)
