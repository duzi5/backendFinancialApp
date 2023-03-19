from flask_sqlalchemy import SQLAlchemy
from brain import app

app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)






class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(25), unique=True)
    sobrenome = db.Column(db.String(60), unique=True)
    email = db.Column(db.String(80), unique=True)

    def __init__(self):