from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from datetime import datetime
from db import mongo
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

moves_blueprint = Blueprint("moves", __name__)

db = mongo.Financial
moves_collection = db["moves"]

def get_month_options(user_id):
    moves_collection = mongo.Financial.moves
    month_options = moves_collection.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$reference_month_year"}}
    ])
    return [month_option["_id"] for month_option in month_options]

@moves_blueprint.route("/create", methods=["POST"])
@jwt_required()
def create_movement():
    move_data = request.get_json()

    if not move_data:
        return jsonify({'error': 'No data provided'}), 400


    user_id = get_jwt_identity()['user_id']


    users_collection = mongo.Financial.users
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({'error': 'User not found'}), 404

    family_name = user["family"]


    families_collection = mongo.Financial.families
    family = families_collection.find_one({"name": family_name})

    if not family:
        return jsonify({'error': 'Family not found'}), 404

    family_id = str(family["_id"])
    installments = int(move_data.get('installments', 1))

    try:
        for i in range(installments):
            print(f"2. Processing installment {i + 1}")
            move_date = datetime.strptime(move_data["date"], "%Y-%m-%d")
            move = {
                "description": move_data["description"],
                "value": move_data["value"],
                "nature": move_data["nature"],
                "user_id": get_jwt_identity()['user_id'],
                "family_id": family_id,
                "date": move_date,
                "reference_month_year": move_date.strftime("%m/%Y"),
            }

            if move_data["nature"] == "negative":
                print("3. Handling negative nature")  # Debug log
                move.update({
                    "category": move_data["category"],
                    "payment_method": move_data["paymentMethod"],
                    "installments": installments,
                })

            if installments > 1:
                print("4. Handling multiple installments")  # Debug lo
                move["installment_number"] = i + 1
                installment_date = move["date"]
                year_offset, new_month = divmod(installment_date.month - 1 + i, 12) # Subtrair 1 antes de usar divmod
                installment_date = installment_date.replace(year=installment_date.year + year_offset, month=new_month + 1) # Adicionar 1 após usar divmod
                move["date"] = installment_date.isoformat().split('T')[0]
                move["installmentInfo"] = f"Parcela {i + 1} de {installments}"
                move["value"] = round(float(move_data["value"]) / installments, 2)
                move["reference_month_year"] = installment_date.strftime("%m/%Y")  # Atualizar o mês e ano de referência para parcelas

            print("5. Inserting move into collection")
            moves_collection.insert_one(move)

    except Exception as e:
        print(f"6. Error occurred: {str(e)}")
        return jsonify({'error': f'An error occurred while creating the movement: {str(e)}'}), 500

    return jsonify({'message': 'Movimentação criada com sucesso!'}), 201

@moves_blueprint.route('/month/<referenceMonth>', methods=['GET'])
@jwt_required()
def get_moves_by_month(referenceMonth):
    user_id = get_jwt_identity()['user_id']
    
    # Buscar movimentos no banco de dados MongoDB
    moves = mongo.Financial.moves.find({'user_id': user_id})

    # Filtrar os movimentos pelo mês de referência
    filtered_moves = [
        move for move in moves
        if move['date'].strftime('%Y-%m') == referenceMonth
    ]

    return jsonify(filtered_moves), 200

@moves_blueprint.route('/month-options', methods=['GET'])
@jwt_required()
def month_options():
    user_id = get_jwt_identity()['user_id']
    month_options = get_month_options(user_id)
    return jsonify(month_options), 200

@jwt_required
@moves_blueprint.route("/", methods=["GET"])
def get_all_moves():
    moves_cursor = moves_collection.find()
    all_moves = [move for move in moves_cursor]
    return jsonify(all_moves), 200

@jwt_required
@moves_blueprint.route("/move/<move_id>", methods=["GET"])
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

    result = moves.insert_many(new_moves)
    inserted_ids = [str(id) for id in result.inserted_ids]
    return jsonify(inserted_ids), 201