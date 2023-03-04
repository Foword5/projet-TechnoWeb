from flask import Flask, jsonify, request
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

#get order
@app.route('/order/<id>', methods=['GET'])
def get_order(id):
    try:
        order = Order.get(Order.id == id)
        #jsonify the order
        order = model_to_dict(order)
        #if credit_card is null or shipping_information is null or transaction is null, replace null value with an empty object
        if order["credit_card"] == None:
            order["credit_card"] = {}
        if order["shipping_information"] == None:
            order["shipping_information"] = {}
        if order["transaction"] == None:
            order["transaction"] = {}

        #product is an object with the id of the product and the quantity
        order["product"] = {"id": order["product"]["id"], "quantity": order["quantity"]}
        return jsonify(order)
        
    except Order.DoesNotExist:
        return jsonify(
            { "errors" : 
             { "order": 
              { "code": "not-found", "name": "La commande demandée n'existe pas" } 
                } 
            } ), 422
    
#create new order
@app.route('/order', methods=['POST'])
def create_order():

    #check if the body contains a product with an id and a quantity
    if "product" not in request.json or "id" not in request.json["product"] or "quantity" not in request.json["product"]:
        return jsonify(
            { "errors" : 
             { "product": 
              { "code": "missing-fields", "name": "La création d'une commande nécessite un produit" } 
                } 
            } ), 422
    #check if the quantity is superior or equal to 1
    if request.json["product"]["quantity"] < 1:
        return jsonify(
            { "errors" : 
             { "product": 
              { "code": "missing-fields", "name": "La quantité doit être supérieure ou égale à 1" } 
                } 
            } ), 422
    
    #get the product if it exists
    try:
        product = Product.get(Product.id == request.json["product"]["id"])
    except Product.DoesNotExist:
        return jsonify(
            { "errors" : 
             { "product": 
              { "code": "not-found", "name": "Le produit demandé n'existe pas" } 
                } 
            } ), 422
    if product.in_stock == False :
        return jsonify(
            { "errors" : 
             { "product": 
              { "code": "out-of-inventory", "name": "Le produit demandé n'est pas en inventaire" } 
                } 
            } ), 422
    
    quantity = request.json["product"]["quantity"]
    #calculate the shipping price
    total_price = product.price * quantity
    
    #calculate the shipping price based on the weight of the product
    if product.weight * quantity < 500:
        shipping_price = total_price + 5
    elif product.weight * quantity < 2000:
        shipping_price = total_price + 10
    else:
        shipping_price = total_price + 25

    #create the order
    order = Order.create(
        total_price = total_price,
        shipping_price = shipping_price,
        product = product,
        quantity = quantity
    )
    #return code 302 and the link to the order
    return jsonify(model_to_dict(order)), 302, {'Location': '/order/' + str(order.id)}




@app.cli.command("init-db") # s'exécute avec la commande flask init-db
def init_db():
    db.create_tables([Product, Shipping_Information, Credit_Card, Transaction, Order])

@app.before_first_request # s'exécute entre le démarrage du serveur et le premier appel
def init_products():
    data = urllib.request.urlopen("http://dimprojetu.uqac.ca/~jgnault/shops/products/products.json").read().decode("utf-8")
    products = json.loads(data)
    for product in products["products"]:
        Product.create(**product)
