from brain import app, client
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager
from flask import session
login = LoginManager(app)


@login.user_loader
def load_user(id):
    return User.objects.get(id=id)


class User(UserMixin, client.Document):
    meta = {'collection': 'users'}
    name = client.StringField(default=True)
    last_name = client.StringField(default=True)
    email = client.EmailField(unique=True)
    password_hash = client.StringField(default=True)
    active = client.BooleanField(default=True)
    is_admin = client.BooleanField(default=False)
    is_client = client.BooleanField(default=False)
    is_master = client.BooleanField(default=False)
    is_manager = client.BooleanField(default=False)
    begin_datetime = client.DateTimeField(default=datetime.now())
    last_activity = client.DateTimeField(default=datetime.now())
    family_id = client.IntegerField(default=0)
    renda = client.IntegerField(default=0)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_by_email(cls, email):
        data = client.find_one("users", {"email": email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id(cls, _id):
        data = client.find_one("users", {"_id": _id})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login_valid(email, password):
        verify_user = User.get_by_email(email)
        if verify_user is not None:
            return check_password_hash(verify_user.password_hash, password)
        return False

    @classmethod
    def register(cls, username, email, password):
        user = cls.get_by_email(email)
        if user is None:
            new_user = cls(username, email, password)
            new_user.save_to_mongo()
            session['email'] = email
            return True
        else:
            return False

    def json(self):
        return {
            "username": self.username,
            "email": self.email,
            "_id": self._id,
            "password": self.password
        }

    def save_to_mongo(self):
        client.insert("users", self.json())
