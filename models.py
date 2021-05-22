from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    role = db.Column(db.Integer, db.ForeignKey("user_roles.role_id"))
    step = db.Column(db.Integer);

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    description = db.Column(db.Text)
    type_id = db.Column(db.Integer, db.ForeignKey("product_types.type_id"))
    price = db.Column(db.Integer)
    presence = db.Column(db.Integer)
    photo_url = db.Column(db.String(200))

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))

class Cart_product(db.Model):
    cart_id = db.Column(db.Integer(), db.ForeignKey("cart.id"), primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey("product.id"), primary_key=True)


class Product_types(db.Model):
    type_id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(200))


class User_roles(db.Model):
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(200))