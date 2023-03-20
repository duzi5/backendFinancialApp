from flask import Flask, render_template, request, jsonify, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.collation import Collation
from flask_login import LoginManager, login_required, current_user
import json
from bson.json_util import dumps
from model_mongodb import User


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)


client = MongoClient(
    "mongodb+srv://desenvolvedor:desenvolvedor@financialapp.wwdb8xz.mongodb.net/?retryWrites=true&w=majority")

users = client.financialApp.users

@login_manager.user_loader
def load_user(user_id):
    return users.find_one( {"_id": user_id})


@app.route('/login', methods=["POST"])
def login():
    email = request.json['email']
    senha = request.json['senha']

    user = users.find_one({
        "email": email
    })
    if check_password_hash(user['senha'], senha):
        session = json.loads(dumps(user))
        return redirect('/protegida')
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

@app.route('/protegida')
@login_required
def protegida():

    if current_user.is_autenticated:
        return "tudo bem"
    else:
        return "nao está autenticado"



# @app.route('/inserir movimento')
# @login_required





if __name__ == "__main__":

    app.run(port=3000, debug=True)
