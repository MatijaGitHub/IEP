from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class CategoryProduct(database.Model):
    __tablename__ = "catprod"
    id = database.Column(database.Integer, primary_key=True)
    product_id = database.Column(database.ForeignKey("product.id"), nullable=False)
    category_id = database.Column(database.ForeignKey("category.id"), nullable=False)


class OrderProduct(database.Model):
    __tablename__ = "orderprod"
    id = database.Column(database.Integer, primary_key=True)
    order_id = database.Column(database.ForeignKey("order.id"), nullable=False)
    product_id = database.Column(database.ForeignKey("product.id"), nullable=False)


class Product(database.Model):
    __tablename__ = "product"
    id = database.Column(database.Integer, primary_key=True)
    categories = database.relationship("Category", secondary=CategoryProduct.__table__, back_populates="products")
    orders = database.relationship("Order", secondary=OrderProduct.__table__, back_populates="products")
    name = database.Column(database.String(256), nullable=False)
    price = database.Column(database.Float, nullable=False)
    amount = database.Column(database.Integer, nullable=False)


class Category(database.Model):
    __tablename__ = "category"
    id = database.Column(database.Integer, primary_key=True)
    category_name = database.Column(database.String(256), nullable=False)
    products = database.relationship("Product", secondary=CategoryProduct.__table__, back_populates="categories")


class Order(database.Model):
    __tablename__ = "order"
    id = database.Column(database.Integer, primary_key=True)
    products = database.relationship("Product", secondary=OrderProduct.__table__, back_populates="orders")
    totalPrice = database.Column(database.Integer, nullable=False)
    status = database.Column(database.Boolean, nullable=False)
    timestamp = database.Column(database.DateTime, nullable=False)
