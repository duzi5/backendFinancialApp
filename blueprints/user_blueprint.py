from email.errors import InvalidDateDefect
from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from datetime import datetime
from db import mongo
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash
from flask_cors import CORS
from base64 import b64decode
import os


user_blueprint = Blueprint("users", __name__)

db = mongo.Financial
users_collection = db["users"]


UPLOAD_FOLDER = 'imagens/avatars'





@jwt_required
@user_blueprint.route('/all', methods=['GET'])
def get_users():
    users_cursor = mongo.db.users.find()
    users = [user for user in users_cursor]

    response = jsonify(users)
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response, 200

@jwt_required
@user_blueprint.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if user:
            response = jsonify(user)
            response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
        else:
            return jsonify({'error': 'User not found'})
    except InvalidDateDefect:
        return jsonify({'error': 'Invalid user ID'})

@jwt_required
@user_blueprint.route("/", methods=["PUT"])
def update_user(user_id):
    users = mongo.db.users
    user = users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    updates = {}
    for field in ["is_consultor", "is_manager", "is_client", "is_master", "birthdate", "family"]:
        if request.json.get(field) is not None:
            updates[field] = request.json.get(field)

    users.update_one({"_id": ObjectId(user_id)}, {"$set": updates})

    response = jsonify({"_id": user_id})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response, 200

@jwt_required
@user_blueprint.route("/", methods=["DELETE"])
def delete_user(user_id):
    users = mongo.db.users
    result = users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "User not found"}), 404

    response = jsonify({"_id": user_id})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response