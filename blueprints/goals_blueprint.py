from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from db import mongo
from datetime import datetime

goals_blueprint = Blueprint("goals_blueprint", __name__)

@goals_blueprint.route("/goals", methods=["GET"])
@jwt_required()
def list_goals():
    current_user_id = get_jwt_identity()['user_id']
    current_family = mongo.Financial.users.find_one(
        {"_id": ObjectId(current_user_id)})["family"]
    goals = mongo.Financial.families.find_one({"name": current_family})["goals"]
    return jsonify(goals), 200


@goals_blueprint.route("/goals", methods=["POST"])
@jwt_required()
def add_goal():
    current_user_id = get_jwt_identity()["user_id"]
    current_user = mongo.Financial.users.find_one(
        {"_id": ObjectId(current_user_id)})
    current_family = current_user["family"]
    data = request.json

    new_goal = {
        "title": data["title"],
        "creation_date": datetime.now(),
        "dueDate": data["dueDate"],
        "description": data["description"],
        "priority": data["priority"],
        "created_by": current_user_id,
        "status": "Não Iniciado",
        "balance": 0,
        "target_value": data['targetValue']
    }

    result = mongo.Financial.families.update_one(
        {"name": current_family}, {"$push": {"goals": new_goal}})

    if result.modified_count == 1:
        return jsonify({"status": "success", "message": "Goal added successfully."}), 201
    else:
        return jsonify({"status": "fail", "message": "Failed to add goal."}), 500


@ goals_blueprint.route("/goals/<goal_id>", methods=["PUT"])
@ jwt_required()
def update_goal(goal_id):
    current_user_id = get_jwt_identity()['user_id']
    current_user = mongo.Financial.users.find_one(
        {"_id": ObjectId(current_user_id)})
    current_family = current_user["family"]
    data = request.json

    updated_goal = {
        "creation_date": data["creation_date"],
        "deadline_date": data["deadline_date"],
        "balance": data["balance"],
        "target": data["target"],
        "description": data["description"]
    }

    result = mongo.Financial.families.update_one(
        {"name": current_family, "goals._id": ObjectId(goal_id)}, {"$set": {"goals.$": updated_goal}})

    if result.modified_count == 1:
        return jsonify({"status": "success", "message": "Goal updated successfully."}), 200
    else:
        return jsonify({"status": "fail", "message": "Failed to update goal."}), 500


@ goals_blueprint.route("/goals/<goal_id>", methods=["DELETE"])
@ jwt_required()
def delete_goal(goal_id):
    current_user_id = get_jwt_identity()['user_id']
    current_user = mongo.Financial.users.find_one(
        {"_id": ObjectId(current_user_id)})
    current_family = current_user["family"]

    result = mongo.Financial.families.update_one(
        {"name": current_family}, {"$push": {"goals": new_goal}})

    if result.modified_count == 1:
        return jsonify({"status": "success", "message": "Goal deleted successfully."}), 200
    else:
        return jsonify({"status": "fail", "message": "Failed to delete goal."}), 500
