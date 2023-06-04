from db import mongo

class PaymentMethod:
    collection = mongo.db.payment_methods

    @classmethod
    def create(cls, data, current_user_id, family_id):
        new_payment_method = {
            "user_id": current_user_id,
            "family_id": family_id,
            "type": data["type"],
            "brand": data["brand"],
            "bank": data["bank"],
            "lastFourDigits": data["lastFourDigits"],
            "best_purchase_day": data["best_purchase_day"],
            "due_date": data["due_date"],
            "creation_date": datetime.now(),
            "last_access": None,
            "notifications": []
        }
        payment_method_id = cls.collection.insert_one(new_payment_method).inserted_id
        return payment_method_id

    @classmethod
    def get_by_id(cls, payment_method_id):
        return cls.collection.find_one({"_id": payment_method_id})

    @classmethod
    def update(cls, payment_method_id, data):
        cls.collection.update_one(
            {"_id": payment_method_id},
            {"$set": data}
        )

    @classmethod
    def delete(cls, payment_method_id):
        cls.collection.delete_one({"_id": payment_method_id})
