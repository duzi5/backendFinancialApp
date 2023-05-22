from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from db import mongo


payment_methods = Blueprint("payment_methods", __name__)

@jwt_required()
@payment_methods.route("/payment_methods", methods=["POST"])
def add_payment_method():
    data = request.get_json()

    current_user_id = get_jwt_identity()['user_id']
    current_user = mongo.Financial.users.find_one({"_id": current_user_id})
    current_family = current_user["family"]

    if "type" not in data or "brand" not in data or "bank" not in data:
        return jsonify({"message": "Type, brand, and bank are required"}), 400

    best_purchase_day = data.get("best_purchase_day", "")
    due_date = data.get("due_date", "")

    if best_purchase_day and (not best_purchase_day.isdigit() or int(best_purchase_day) < 1 or int(best_purchase_day) > 30):
        return jsonify({"message": "Invalid best_purchase_day value. Must be a number between 1 and 30."}), 400

    if due_date and (not due_date.isdigit() or int(due_date) < 1 or int(due_date) > 30):
        return jsonify({"message": "Invalid due_date value. Must be a number between 1 and 30."}), 400

    payment_method = {
        "_id": ObjectId(),
        "type": data["type"],
        "brand": data["brand"],
        "name": data["name"],
        "bank": data["bank"],
        "best_purchase_day": best_purchase_day,
        "due_date": due_date,
        "saldo": 0,
        "family": current_family
    }

    mongo.Financial.payment_methods.insert_one(payment_method)

    mongo.Financial.families.update_one(
        {"name": current_family},
        {"$push": {"payment_methods": payment_method["_id"]}}
    )

    return jsonify({"message": "Payment method added successfully"})


@jwt_required()
@payment_methods.route("/payment_methods", methods=["GET"])
def get_payment_methods():
    current_user_id = get_jwt_identity()['user_id']
    current_user = mongo.Financial.users.find_one({"_id": current_user_id})
    current_family = current_user["family"]

    payment_methods = mongo.Financial.payment_methods.find({"family": current_family}, {"family": 0})

    payment_methods_list = []
    for payment_method in payment_methods:
        payment_methods_list.append({
            "id": str(payment_method["_id"]),
            "type": payment_method["type"],
            "brand": payment_method["brand"],
            "name": payment_method["name"],
            "bank": payment_method["bank"],
            "best_purchase_day": payment_method["best_purchase_day"],
            "due_date": payment_method["due_date"],
            "saldo": payment_method["saldo"],
        })

    return jsonify(payment_methods_list)

