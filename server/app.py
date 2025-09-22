#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# Index route
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Route to get all restaurants
class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        # Pass include_pizzas=False to exclude restaurant_pizzas in the list of restaurants
        return [restaurant.to_dict(include_pizzas=False) for restaurant in restaurants], 200

# Route to get a single restaurant by ID
class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        # Pass include_pizzas=True to include the restaurant_pizzas
        return restaurant.to_dict(include_pizzas=True), 200

# Route to delete a restaurant by ID
class DeleteRestaurant(Resource):
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        # Delete associated RestaurantPizzas first (if cascade deletes aren't set)
        for rp in restaurant.restaurant_pizzas:
            db.session.delete(rp)
        
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

# Route to get all pizzas
class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict() for pizza in pizzas], 200

# Route to create a new restaurant_pizza
class RestaurantPizzaCreate(Resource):
    def post(self):
        data = request.get_json()
        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        # Validate the price
        if price < 1 or price > 30:
            return {"errors": ["validation errors"]}, 400

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not pizza or not restaurant:
            return {"error": "Pizza or Restaurant not found"}, 404

        # Create and add the new RestaurantPizza
        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza.id, restaurant_id=restaurant.id)
        db.session.add(restaurant_pizza)
        db.session.commit()

        return restaurant_pizza.to_dict(), 201

# Registering routes with Flask-RESTful API
api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantByID, '/restaurants/<int:id>')
api.add_resource(DeleteRestaurant, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzaCreate, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
