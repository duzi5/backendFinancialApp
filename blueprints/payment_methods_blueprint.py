from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from db import mongo

payment_methods = Blueprint("payment_methods", __name__)

@payment_methods.route("/payment_methods", methods=["GET"])
@jwt_required()
def get_payment_methods():
    current_user_id = get_jwt_identity()
    
    current_user = mongo.Financial.users.find_one({"_id": ObjectId(current_user_id['user_id'])})
    current_family_id = str(current_user["family"])
    family = mongo.Financial.families.find_one({"_id": ObjectId(current_family_id)})
    payment_methods = family["payment_methods"]
    result = []

    for payment_method in payment_methods:
        result.append({
            "_id": str(payment_method["_id"]),
            "type": payment_method["type"],
            "brand": payment_method["brand"],
            "bank": payment_method["bank"],
            "best_purchase_day": payment_method["best_purchase_day"],
            "due_date": payment_method["due_date"],
        })

    return jsonify(result), 200


@payment_methods.route("/payment_methods", methods=["POST"])
@jwt_required()
def add_payment_method():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    current_user = mongo.Financial.users.find_one({"_id":str(ObjectId(current_user_id['user_id']))})# Verificação de dados obrigatórios
    if "type" not in data or "brand" not in data or "bank" not in data:
        return jsonify({"message": "Type, brand and bank are required"}), 400

    payment_method = {
         "user_id": str(ObjectId(current_user_id['user_id'])),
        "family_id": str(ObjectId(current_user['family'])),
        "type": data["type"],
        "brand": data["brand"],
        "bank": data["bank"],
        "best_purchase_day": data.get("best_purchase_day", ""),
        "due_date": data.get("due_date", ""),
    }

    mongo.Financial.families.update_one(
        {"_id": ObjectId(current_user['family'])},
        {"$push": {"payment_methods": payment_method}}
    )
    mongo.Financial.payment_methods.insert_one({
        "user_id": str(ObjectId(current_user_id['user_id'])),
        "family_id": str(ObjectId(current_user['family'])),
        "type": data["type"],
        "brand": data["brand"],
        "bank": data["bank"],
        "best_purchase_day": data.get("best_purchase_day", ""),
        "due_date": data.get("due_date", "")
    })
    return jsonify({"message": "Payment method added successfully"})


@payment_methods.route("/payment_methods/<id>", methods=["PUT"])
@jwt_required()
def update_payment_method(id):
    data = request.get_json()
    current_user_id = get_jwt_identity()
    current_user = mongo.Financial.users.find_one({"_id": ObjectId(current_user_id._id)})
    current_family_id = str(current_user["family"])
    
    mongo.Financial.families.update_one(
        {"_id": ObjectId(current_family_id), "payment_methods._id": str(ObjectId(id))},
        {"$set": {"payment_methods.$": data}}
    )
    mongo.Financial.payment_methods.update_one(
        {"_id": ObjectId(id)},
        {"$set": data}
    )
    return jsonify({"message": "Payment method updated successfully"})

@payment_methods.route("/payment_methods/<id>", methods=["DELETE"])
@jwt_required()
def delete_payment_method(id):
    current_user_id = get_jwt_identity()
    current_user = mongo.Financial.users.find_one({"_id": ObjectId(current_user_id._id)})
    current_family_id = str(current_user["family"])
    
    mongo.Financial.families.update_one(
        {"_id": ObjectId(current_family_id)},
        {"$pull": {"payment_methods": {"_id": ObjectId(id)}}}
    )
    mongo.Financial.payment_methods.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "Payment method deleted successfully"})

@payment_methods.route("/payment_methods_list", methods=["GET"])
@jwt_required()
def get_family_payment_methods():
    current_user_id = get_jwt_identity()
    print(current_user_id)
    current_user = mongo.Financial.users.find_one({"_id": ObjectId(current_user_id.id)})
    current_family_id = str(current_user["family"])
    
    payment_methods = mongo.Financial.payment_methods.find({"family": ObjectId(current_family_id)})
    result = []

    for payment_method in payment_methods:
        result.append({
            "_id": str(payment_method["_id"]),
            "type": payment_method["type"],
            "brand": payment_method["brand"],
            "bank": payment_method["bank"],
            "best_purchase_day": payment_method["best_purchase_day"],
            "due_date": payment_method["due_date"],
        })

    return jsonify(result)
