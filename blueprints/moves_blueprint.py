from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from datetime import datetime
from db import mongo
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from dateutil.relativedelta import relativedelta

moves_blueprint = Blueprint("moves", __name__)
db = mongo.Financial
moves_collection = db["moves"]


@moves_blueprint.route("/", methods=["GET"])
@jwt_required
def get_all_moves():
    moves_cursor = moves_collection.find()
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


@jwt_required
@moves_blueprint.route("/create_multiple", methods=["POST"])
def create_multiple_moves():

    moves_data = request.json["moves"]

    new_moves = []
    for move_data in moves_data:
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

        new_moves.append(move)

    result = moves_collection.insert_many(new_moves)
    inserted_ids = [str(id) for id in result.inserted_ids]
    return jsonify(inserted_ids), 201


@jwt_required()
@moves_blueprint.route("/add_move", methods=["POST"])
def add_move():
    user_id = get_jwt_identity()["user_id"]
    move_data = request.get_json()

    user = mongo.Financial.users.find_one({"_id": ObjectId(user_id)})
    family_name = user["family"]
    family = mongo.Financial.families.find_one({"name": family_name})
    family_id = family["_id"]

    if move_data.get("reserve", False):
        balance_goals = move_data.get("balance_goals", [])
        for goal in balance_goals:
            if goal.get("payment_method") is None or goal.get("value") is None:
                return jsonify({"message": "Os campos 'payment_method' e 'value' são obrigatórios para adicionar metas."}), 400

        move_data["reserve"] = True
        move_data["balance_goals"] = balance_goals
    else:
        move_data["reserve"] = False
        move_data.pop("balance_goals", None)

    if "installments" in move_data and move_data["installments"] > 1:
        moves = []
        installment_info = move_data.pop("installment_info")
        date = datetime.strptime(move_data["date"], "%Y-%m-%d")

        for i in range(move_data["installments"]):
            installment_date = date + relativedelta(months=1 * i)
            installment_data = {
                "description": move_data["description"],
                "value": move_data["value"] / move_data["installments"],
                "nature": move_data["nature"],
                "category": move_data["category"],
                "payment_method": move_data["payment_method"],
                "date": installment_date.strftime("%Y-%m-%d"),
                "installment_info": f"{i+1}-{move_data['installments']}",
                "family_id": family_id,
                "reserve": move_data["reserve"],
                "reference_month_year": f"{installment_date.month}-{installment_date.year}"
            }
            moves.append(installment_data)

        mongo.Financial.moves.insert_many(moves)
        return jsonify({"message": "Movimentação adicionada com sucesso"}), 201
    else:
        move_data["date"] = datetime.strptime(move_data["date"], "%Y-%m-%d")
        move_data["family_id"] = family_id
        move_data["reference_month_year"] = f"{move_data['date'].month}-{move_data['date'].year}"
        mongo.Financial.moves.insert_one(move_data)
        return jsonify({"message": "Movimentação adicionada com sucesso"}), 201


@jwt_required
@moves_blueprint.route("/<string:reference_month_year>/<string:payment_method>", methods=["GET"])
def get_moves(reference_month_year, payment_method):

    user_id = get_jwt_identity()["user_id"]

    # Filtrar os movimentos do usuário pelo reference_month_year e payment_method
    filtered_movements = []

    # Lógica para filtrar os movimentos com base no reference_month_year e payment_method
    cursor = moves_collection.find(
        {
            "user_id": user_id,
            "reference_month_year": reference_month_year,
            "payment_method": payment_method
        }
    )

    for movement in cursor:
        movement["_id"] = str(movement["_id"])
        filtered_movements.append(movement)

    return jsonify(filtered_movements)


@jwt_required
@moves_blueprint.route("/month/<string:reference_month>/payment_method/<string:payment_method_id>", methods=["GET"])
def get_moves_by_month_and_payment_method(reference_month, payment_method_id):
    moves = []
    for move in moves_collection.find({"reference_month_year": reference_month.replace('/', '-'), "payment_method_id": payment_method_id}):
        move["_id"] = str(move["_id"])
        moves.append(move)
    return jsonify(moves)

@jwt_required
@moves_blueprint.route("/month-options/payment_method/<string:payment_method_id>", methods=["GET"])
def get_month_options_by_payment_method(payment_method_id):
    month_options = []
    for move in moves_collection.find({"payment_method_id": payment_method_id}):
        reference_month_year = move["reference_month_year"]
        if reference_month_year not in month_options:
            month_options.append(reference_month_year)
    return jsonify(month_options)

    