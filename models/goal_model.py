from db import mongo
from datetime import datetime

class Goal:
    collection = mongo.db.goals

    @classmethod
    def create(cls, data, current_user_id):
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
        goal_id = cls.collection.insert_one(new_goal).inserted_id
        return goal_id

    @classmethod
    def update_status(cls, goal_id, new_status):
        cls.collection.update_one(
            {"_id": goal_id},
            {"$set": {"status": new_status}}
        )

    @classmethod
    def update_balance(cls, goal_id, new_balance):
        cls.collection.update_one(
            {"_id": goal_id},
            {"$set": {"balance": new_balance}}
        )

    @classmethod
    def get(cls, goal_id):
        return cls.collection.find_one({"_id": goal_id})
