from flask import Flask, jsonify, request, abort, redirect, url_for
from playhouse.shortcuts import model_to_dict, dict_to_model
from models import *

app = Flask(__name__)

@app.route('/')
def products():
    return jsonify([model_to_dict(product) for product in Product.select()])

    
    
   


@app.cli.command("init-db")
def init_db():
    db.create_tables([Product, Shipping_Information, Credit_Card, Transaction, Order])
