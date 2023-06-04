from flask import Blueprint, request, jsonify
from datetime import datetime
from db import mongo
from bson.objectid import ObjectId

user_collection = mongo.Financial.users
moves_collection = mongo.Financial.moves
family_collection = mongo.Financial.families

family_bp = Blueprint('family_bp', __name__)

@family_bp.route('/family', methods=['POST'])
def create_family():
    family_data = request.get_json()

    new_family = {
        'creation_date': datetime.utcnow(),
        'name': family_data['name'],
        'goals': family_data['goals'],
        'payment_methods_ids': family_data['payment_methods_ids'],
        'members_ids': family_data['members_ids']
    }

    inserted_family = family_collection.insert_one(new_family)

    return jsonify({"id": str(inserted_family.inserted_id)}), 201


@family_bp.route('/family/<string:family_id>', methods=['GET'])
def get_family(family_id):
    try:
        family = family_collection.find_one({"_id": ObjectId(family_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if family is None:
        return jsonify({"error": "Family not found"}), 404

    # Converte o ObjectId para uma string
    family['_id'] = str(family['_id'])

    return jsonify(family), 200


@family_bp.route('/families', methods=['GET'])
def get_all_families():
    try:
        families = list(family_collection.find())
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if not families:
        return jsonify({"error": "No families found"}), 404

    # Converte o ObjectId para uma string
    for family in families:
        family['_id'] = str(family['_id'])

    return jsonify(families), 200


@family_bp.route('/family/user/<string:user_id>', methods=['GET'])
def get_user_family(user_id):
    try:
        user = user_collection.find_one({"_id": ObjectId(user_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if user is None:
        return jsonify({"error": "User not found"}), 404

    family_id = user.get("family_id")

    if not family_id:
        return jsonify({"error": "User does not belong to a family"}), 404

    try:
        family = family_collection.find_one({"_id": ObjectId(family_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if family is None:
        return jsonify({"error": "Family not found"}), 404

    # Converte o ObjectId para uma string
    family['_id'] = str(family['_id'])

    return jsonify(family), 200

@family_bp.route('/family/members/<string:family_id>', methods=['GET'])
def get_family_members(family_id):
    try:
        family = family_collection.find_one({"_id": ObjectId(family_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if family is None:
        return jsonify({"error": "Family not found"}), 404

    member_ids = family.get("members_ids", [])

    members = []
    for member_id in member_ids:
        try:
            member = user_collection.find_one({"_id": ObjectId(member_id)})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

        if member is not None:
            member['_id'] = str(member['_id'])  # Convert ObjectId to string
            members.append(member)

    return jsonify(members), 200






