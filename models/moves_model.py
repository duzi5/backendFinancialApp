from db import mongo
from datetime import datetime


class Move:
    collection = mongo.db.moves

    @classmethod
    def create(cls, data, user_id, family_id):
        new_move = {
            "user_id": user_id,
            "family_id": family_id,
            "title": data["title"],
            "creation_date": datetime.now(),
            "dueDate": data["dueDate"],
            "description": data["description"],
            "priority": data["priority"],
            "created_by": user_id,
            "status": "Não Iniciado",
            "balance": 0,
            "target_value": data['targetValue']
        }
        move_id = cls.collection.insert_one(new_move).inserted_id
        return move_id

    @classmethod
    def get_by_id(cls, move_id):
        return cls.collection.find_one({"_id": move_id})

    @classmethod
    def update(cls, move_id, data):
        cls.collection.update_one(
            {"_id": move_id},
            {"$set": data}
        )

    @classmethod
    def delete(cls, move_id):
        cls.collection.delete_one({"_id": move_id})
