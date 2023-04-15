from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from datetime import datetime
from db import mongo
from flask_jwt_extended import jwt_required


moves_blueprint = Blueprint("moves", __name__)

db = mongo.Financial
moves = db["moves"]

@jwt_required
@moves_blueprint.route("/create", methods=["POST"])
def create_move():
    move_data = request.json

    move = {
        "description": move_data["description"],
        "value": move_data["value"],
        "nature": move_data["nature"],
        "user_id": move_data["user_id"],
        "family_id": move_data["family_id"],
        "date": datetime.strptime(move_data["date"], "%Y-%m-%d"),
    }

    if move_data["nature"] == "negative":
        move.update({
            "category": move_data["category"],
            "payment_method": move_data["payment_method"],
            "installments": move_data["installments"],
            "installment_number": move_data["installment_number"],
            "installment_value": move_data["installment_value"]
        })

    move_id = moves.insert_one(move).inserted_id
    return jsonify(str(move_id)), 201

@jwt_required
@moves_blueprint.route("/", methods=["GET"])
def get_all_moves():
    moves_cursor = moves.find()
    all_moves = [move for move in moves_cursor]
    return jsonify(all_moves), 200

@jwt_required
@moves_blueprint.route("/<move_id>", methods=["GET"])
def get_move(move_id):
    move = moves.find_one({"_id": ObjectId(move_id)})
    if move:
        return jsonify(move), 200
    else:
        return jsonify({"error": "Move not found"}), 404

@jwt_required
@moves_blueprint.route("/<move_id>", methods=["PUT"])
def update_move(move_id):
    updates = request.json
    moves.update_one({"_id": ObjectId(move_id)}, {"$set": updates})
    return jsonify({"msg": "Move updated successfully"}), 200

@jwt_required
@moves_blueprint.route("/<move_id>", methods=["DELETE"])
def delete_move(move_id):
    result = moves.delete_one({"_id": ObjectId(move_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Move not found"}), 404
    return jsonify({"msg": "Move deleted successfully"}), 200
