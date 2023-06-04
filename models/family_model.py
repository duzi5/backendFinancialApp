from db import mongo
from datetime import datetime

class Family:
    collection = mongo.db.families

    @classmethod
    def create(cls, members, payment_methods_ids, notifications):
        data = {
            "members": members,
            "payment_methods_ids": payment_methods_ids,
            "created_at": datetime.utcnow(),
            "last_accessed_at": None,
            "notifications": notifications
        }
        family_id = cls.collection.insert_one(data).inserted_id
        return family_id

    @classmethod
    def update_last_accessed_at(cls, family_id):
        cls.collection.update_one(
            {"_id": family_id},
            {"$set": {"last_accessed_at": datetime.utcnow()}}
        )

    @classmethod
    def get(cls, family_id):
        return cls.collection.find_one({"_id": family_id})
