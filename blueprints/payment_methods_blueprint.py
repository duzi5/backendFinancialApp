from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from db import mongo


payment_methods = Blueprint("payment_methods", __name__)


from bson import ObjectId

@payment_methods.route('/<family_id>/<payment_method_id>', methods=['GET'])
def get_payment_method(family_id, payment_method_id):
    family = mongo.Fiancial.families.find_one({'_id': ObjectId(family_id)})
    if not family:
        return jsonify({'error': 'Família não encontrada'}), 404

    payment_method = next(
        (method for method in family['payment_methods'] if method['_id'] == ObjectId(payment_method_id)),
        None
    )
    if not payment_method:
        return jsonify({'error': 'Método de pagamento não encontrado'}), 404

    return jsonify(payment_method), 200




@payment_methods.route("/payment_methods", methods=["GET"])
@jwt_required()
def get_payment_methods():
    current_user_id = get_jwt_identity()["user_id"]
    current_user = mongo.Financial.users.find_one({"_id": ObjectId(current_user_id)})
    current_family_name = current_user["family"]
    family = mongo.Financial.families.find_one({"name": current_family_name})
    payment_methods = family["payment_methods"]
    result = []
    print(payment_methods)
    for payment_method in payment_methods:
        
        result.append({
        "_id": str(payment_method["_id"]),
        "type": payment_method["type"],
        "name": payment_method["name"],
        "brand": payment_method["brand"],
        "bank": payment_method["bank"],
        "best_purchase_day": payment_method["best_purchase_day"],
        "due_date": payment_method["due_date"],
        "saldo": payment_method["saldo"]
        })

    return jsonify(result), 200


@payment_methods.route("/payment_methods", methods=["POST"])
@jwt_required()
def add_payment_method():
    data = request.get_json()

    print(get_jwt_identity())

    current_user_id = get_jwt_identity()['user_id']
    print(current_user_id)

    if not isinstance(current_user_id, ObjectId):
        current_user_id = ObjectId(current_user_id)
    current_user = mongo.Financial.users.find_one({"_id": current_user_id})
    current_family= current_user["family"]

    if "type" not in data or "brand" not in data or "bank" not in data:
        return jsonify({"message": "Type, brand, and bank are required"}), 400

    payment_method = {
        "_id": ObjectId(),
        "type": data["type"],
        "brand": data["brand"],
        "name": data["name"],
        "bank": data["bank"],
        "best_purchase_day": data.get("best_purchase_day", ""),
        "due_date": data.get("due_date", ""),
        "saldo": 0
    }

    mongo.Financial.families.update_one(
        {"name": current_family  },
        {"$push": {"payment_methods": payment_method}}
    )

    return jsonify({"message": "Payment method added successfully"})



@payment_methods.route("/payment_methods/<id>", methods=["PUT"])
@jwt_required()
def update_payment_method(id):
    data = request.get_json()
    current_user_id = get_jwt_identity()
    current_user = mongo.Financial.users.find_one({"_id": ObjectId(current_user_id['_id'])})
    current_family_id = current_user["family"]

    if not data:
        return jsonify({"message": "No data provided to update"}), 400

    update_data = {}
    for key, value in data.items():
        update_data[f"payment_methods.$.{key}"] = value

    mongo.Financial.families.update_one(
        {"_id": ObjectId(current_family_id), "payment_methods._id": ObjectId(id)},
        {"$set": update_data}
    )

    return jsonify({"message": "Payment method updated successfully"})

@payment_methods.route("/payment_methods/<id>", methods=["DELETE"])
@jwt_required()
def delete_payment_method(id):
    current_user_id = get_jwt_identity()
    current_user = mongo.Financial.users.find_one({"_id": ObjectId(current_user_id['user_id'])})
    current_family_name = current_user["family"]

    mongo.Financial.families.update_one(
        {"name": current_family_name},
        {"$pull": {"payment_methods": {"_id": ObjectId(id)}}}
    )

    return jsonify({"message": "Payment method deleted successfully"})

