from flask import Blueprint, request, jsonify
from datetime import datetime
from db import mongo
from bson.objectid import ObjectId

family_bp = Blueprint('family_bp', __name__)

family_collection = mongo.Financial.families

@family_bp.route('/family', methods=['POST'])
def create_family():
    family_data = request.get_json()

    new_family = {
        'creation_date': datetime.utcnow(),
        'name': family_data['name'],
        'goals': family_data['goals'],
        'payment_methods': family_data['payment_methods'],
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
    print(jsonify(families))
    return jsonify(families), 200
