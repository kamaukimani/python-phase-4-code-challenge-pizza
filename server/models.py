from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from flask import Flask
from marshmallow import fields

db = SQLAlchemy()

class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # Relationship with RestaurantPizza, using 'restaurant_pizza' as backref
    restaurant_pizzas = db.relationship('RestaurantPizza', backref='restaurant_pizza', cascade='all, delete-orphan')

    def to_dict(self, include_pizzas=False):
        restaurant_data = {
            'id': self.id,
            'name': self.name,
            'address': self.address
        }
        if include_pizzas:
            restaurant_data['restaurant_pizzas'] = [rp.to_dict() for rp in self.restaurant_pizzas]
        return restaurant_data


class Pizza(db.Model):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # Relationship with RestaurantPizza, changing backref to avoid conflict
    restaurant_pizzas = db.relationship('RestaurantPizza', backref='pizza_items')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients
        }


class RestaurantPizza(db.Model):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    # Relationships to Pizza and Restaurant
    pizza = db.relationship('Pizza', backref='restaurant_pizzas')  # Relationship to Pizza model
    restaurant = db.relationship('Restaurant', backref='restaurant_pizza')  # Relationship to Restaurant model

    def to_dict(self):
        return {
            'id': self.id,
            'pizza_id': self.pizza_id,
            'restaurant_id': self.restaurant_id,
            'price': self.price,
            'pizza': self.pizza.to_dict(),
            'restaurant': self.restaurant.to_dict()
        }
