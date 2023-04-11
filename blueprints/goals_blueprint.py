from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from db import mongo
from flask_cors import CORS

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@jwt_required()
@goals_bp.route("/", methods=["GET"])
def get_goals():
    user_id = get_jwt_identity()
    goals = mongo.Financial.goals.find({"user_id": user_id})
    result = []
    for goal in goals:
        goal["_id"] = str(goal["_id"])
        result.append(goal)
    return jsonify(result), 200

@jwt_required()
@goals_bp.route("/", methods=["POST"])
def create_goal():
    user_id = get_jwt_identity()
    family_id = request.json["family_id"]
    description = request.json["description"]
    deadline = request.json["deadline"]
    amount = request.json["amount"]
    priority_level = request.json["priority_level"]
    created_at = datetime.utcnow()

    goal = {
        "user_id": user_id,
        "family_id": family_id,
        "description": description,
        "deadline": deadline,
        "amount": amount,
        "priority_level": priority_level,
        "created_at": created_at,
    }
    mongo.Financial.goals.insert_one(goal)
    goal["_id"] = str(goal["_id"])
    return jsonify(goal), 201

@jwt_required()
@goals_bp.route("/<goal_id>", methods=["GET"])
def get_goal(goal_id):
    from bson.objectid import ObjectId
    user_id = get_jwt_identity()
    goal = mongo.Financial.goals.find_one({"_id": ObjectId(goal_id), "user_id": user_id})
    if goal:
        goal["_id"] = str(goal["_id"])
        return jsonify(goal), 200
    else:
        return jsonify({"error": "Goal not found"}), 404

@jwt_required()
@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    from bson.objectid import ObjectId
    user_id = get_jwt_identity()
    goal = mongo.Financial.goals.find_one({"_id": ObjectId(goal_id), "user_id": user_id})
    if goal:
        goal_data = request.json
        update_data = {key: value for key, value in goal_data.items() if key != "_id"}
        mongo.Financial.goals.update_one({"_id": ObjectId(goal_id)}, {"$set": update_data})
        return jsonify({"message": "Goal updated successfully"}), 200
    else:
        return jsonify({"error": "Goal not found"}), 404

@jwt_required()
@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    from bson.objectid import ObjectId
    user_id = get_jwt_identity()
    result = mongo.Financial.goals.delete_one({"_id": ObjectId(goal_id), "user_id": user_id})
    if result.deleted_count:
        return jsonify({"message": "Goal deleted successfully"}), 200
    else:
        return jsonify({"error": "Goal not found"}), 404


