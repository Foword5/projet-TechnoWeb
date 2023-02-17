from flask import Flask, jsonify
from playhouse.shortcuts import model_to_dict, dict_to_model
import urllib.request
import json
from models import *

app = Flask(__name__)

@app.route('/')
def products():
    products = {"products": []}
    for product in Product.select():
        products["products"].append(model_to_dict(product))
    return jsonify(products)

@app.cli.command("init-db")
def init_db():
    db.create_tables([Product, Shipping_Information, Credit_Card, Transaction, Order])

@app.cli.command("init-products")
def init_products():
    data = urllib.request.urlopen("http://dimprojetu.uqac.ca/~jgnault/shops/products/products.json").read().decode("utf-8")
    products = json.loads(data)
    for product in products["products"]:
        Product.create(**product)



