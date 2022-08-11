from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

class User(database.Model):
    __tablename__ = "user"
    id = database.Column(database.Integer, primary_key = True)
    email = database.Column(database.String(256), nullable = True)
    password = database.Column(database.String(256), nullable = False)
    forename = database.Column(database.String(256), nullable = False)
    surname = database.Column(database.String(256), nullable=False)
    my_role = database.Column(database.Integer, database.ForeignKey("role.id"),nullable = False)

class Role(database.Model):
    __tablename__ = "role"
    id = database.Column(database.Integer, primary_key=True)
    role = database.Column(database.String(256), nullable=True)
