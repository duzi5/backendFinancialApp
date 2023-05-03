from functools import wraps
from http import HTTPStatus
from flask import Flask, jsonify, redirect, request, url_for
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
)
from flask_cors import CORS
from flask_jwt_extended import create_access_token
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from blueprints.goals_blueprint import goals_blueprint
from blueprints.user_blueprint import user_blueprint
from blueprints.familys_blueprint import family_bp
from blueprints.moves_blueprint import moves_blueprint
from blueprints.payment_methods_blueprint import payment_methods
from bson import ObjectId
from db import mongo

app = Flask(__name__)

CORS(app)

app.config["MONGO_URI"] = "mongodb+srv://desenvolvedor:desenvolvedor@financialapp.wwdb8xz.mongodb.net/test"
app.config["JWT_SECRET_KEY"] = "jwt-secret-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600000
jwt = JWTManager(app)
app.register_blueprint(user_blueprint, url_prefix="/users")
app.register_blueprint(payment_methods, url_prefix="/payment_methods")
app.register_blueprint(goals_blueprint, url_prefix="/goals")
app.register_blueprint(moves_blueprint, url_prefix="/moves")
app.register_blueprint(family_bp, url_prefix="/families")
CORS(user_blueprint)
CORS(payment_methods)
CORS(goals_blueprint)
CORS(moves_blueprint)
CORS(family_bp)


users_collection = mongo.Financial.users


def generate_access_token(user):
    payload = {'user_id': str(user['_id'])}
    access_token = create_access_token(identity=payload)
    return access_token


@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    user = users_collection.find_one({"email": email})
    if user and check_password_hash(user['password'], password):
        user['_id'] = str(user['_id'])
        access_token = generate_access_token(user)
        response = {
            'access_token': access_token,
            'user': user
        }
        return jsonify(response)
    else:
        return jsonify({'error': 'Invalid email or password'})


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()['user_id']
        users = users_collection.find()
        current_user = users.get(current_user_id, None)
        if not current_user or current_user['type'] != 'admin':
            return jsonify({'msg': 'Usuário não autorizado'}), HTTPStatus.FORBIDDEN
        return func(*args, **kwargs)

    return wrapper


@app.route("/create", methods=["POST"])
def create_user():
    print(request.json)
    existing_user = users_collection.find_one({"email": request.json["email"]})
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 400

    user = request.json
    user["password"] = generate_password_hash(request.json["password"])
    user["email"] = request.json["email"]
    user["name"] = request.json["name"]

    user["is_consultor"] = False
    user["is_manager"] = False
    user["is_client"] = True
    user["is_master"] = False
    user["creation_date"] = datetime.utcnow()

    user_id = users_collection.insert_one(user).inserted_id

    return jsonify({"_id": str(user_id)}), 201


if __name__ == '__main__':
    app.run(debug=True)
