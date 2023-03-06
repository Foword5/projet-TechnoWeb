from flask import Flask, jsonify, request
from playhouse.shortcuts import model_to_dict
import urllib.request
from urllib.error import HTTPError
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
        #delete the quantity key
        del order["quantity"]
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


@app.route('/order/<int:order_id>', methods=["PUT"])
def add_ship(order_id):
    try:
        order = Order.get(Order.id == order_id)
        #jsonify the order
        order = model_to_dict(order)

        #Checking if it is an order or a credit card edit
        if "order" in request.json :
            orderInfo = request.json["order"]

            #Checking if we have all the informations we need
            if ("email" not in orderInfo or 
                "shipping_information" not in orderInfo or 
                "country" not in orderInfo["shipping_information"] or
                "address" not in orderInfo["shipping_information"] or
                "postal_code" not in orderInfo["shipping_information"] or
                "city" not in orderInfo["shipping_information"] or
                "province" not in orderInfo["shipping_information"]) :
                return jsonify({
                    "errors" : {
                        "order": {
                            "code": "missing-fields",
                            "name": "Il manque un ou plusieurs champs qui sont obligatoires",
                            }
                        }
                    } ), 422
            
            #creating new shipping informatin
            shipping_info = Shipping_Information.create(
                country = orderInfo["shipping_information"]["country"],
                address = orderInfo["shipping_information"]["address"],
                postal_code = orderInfo["shipping_information"]["postal_code"],
                city = orderInfo["shipping_information"]["city"],
                province = orderInfo["shipping_information"]["province"]
            )
            
            #Adding the email and the shipping info to the order
            (
                Order.update({"email":orderInfo["email"],"shipping_information":shipping_info})
                .where(Order.id ==order_id)
                .execute()
            )

            order = Order.get(Order.id == order_id)
            #jsonify the order
            order = model_to_dict(order)
            return jsonify(order), 200

        elif "credit_card" in request.json :
            #checking if the order has shipping info
            if order["shipping_information"] == None or order["email"] == None:
                return jsonify({
                "errors" : {
                    "order": {
                        "code": "missing-fields",
                        "name": "Les informations du client sont nécessaire avant d'appliquer une carte de crédit",
                        }
                    }
                } ), 422
            
            #checking if the order has already been payed
            if order["paid"]:
                return jsonify({
                    "errors" : {
                        "order": {
                            "code": "already-paid",
                            "name": "La commande a déjà été payée."
                            }
                        }
                    } ), 422

            creditCardInfo = request.json["credit_card"]

            #Checking if we have all the informations we need
            if ("name" not in creditCardInfo or
                "number" not in creditCardInfo or
                "expiration_year" not in creditCardInfo or
                "cvv" not in creditCardInfo or
                "expiration_month" not in creditCardInfo) :
                return jsonify({
                    "errors" : {
                        "order": {
                            "code": "missing-fields",
                            "name": "Il manque un ou plusieurs champs qui sont obligatoires",
                            }
                        }
                    } ), 422
            
            try:
                #creating the data to send to the payement API
                paymentData = {
                    "credit_card" : creditCardInfo,
                    "amount_charged": order["shipping_price"]
                }

                #asking the payement API if the payement is accepted
                paymenent = urllib.request.urlopen("http://dimprojetu.uqac.ca/~jgnault/shops/pay/", data = json.dumps(paymentData).encode('utf-8'))
                payementInfo = json.loads(paymenent.read().decode("utf-8"))

                #creating the credit card info
                creditCard =  Credit_Card.create(
                    name = payementInfo["credit_card"]["name"],
                    first_digits = payementInfo["credit_card"]["first_digits"],
                    last_digits = payementInfo["credit_card"]["last_digits"],
                    expiration_year = payementInfo["credit_card"]["expiration_year"],
                    expiration_month = payementInfo["credit_card"]["expiration_month"]
                )

                #creating the transaction infos
                transaction = Transaction.create(
                    id = payementInfo["transaction"]["id"],
                    success = payementInfo["transaction"]["success"],
                    amount_charged = payementInfo["transaction"]["amount_charged"]
                )

                #Adding the creadit card info and the transaction info to the order
                (
                    Order.update({"transaction":transaction,"credit_card":creditCard, "paid":payementInfo["transaction"]["success"]})
                    .where(Order.id ==order_id)
                    .execute()
                )

                order = Order.get(Order.id == order_id)
                #jsonify the order
                order = model_to_dict(order)
                return jsonify(order), 200

            except HTTPError as e:
                #if the paymenet is refused, then we send the error
                payementInfo = json.loads(e.read())
                return jsonify(payementInfo), e.code
        
        return jsonify({
                "errors" : {
                    "order": {
                        "code": "missing-fields",
                        "name": "Il manque un ou plusieurs champs qui sont obligatoires",
                        }
                    }
                } ), 422 
        
    except Order.DoesNotExist:
        return jsonify(
            { "errors" : 
             { "order": 
              { "code": "not-found", "name": "La commande demandée n'existe pas" } 
                } 
            } ), 422


@app.cli.command("init-db") # s'exécute avec la commande flask init-db
def init_db():
    db.create_tables([Product, Shipping_Information, Credit_Card, Transaction, Order])

@app.before_first_request # s'exécute entre le démarrage du serveur et le premier appel
def init_products():
    Product.delete().execute()
    data = urllib.request.urlopen("http://dimprojetu.uqac.ca/~jgnault/shops/products/products.json").read().decode("utf-8")
    products = json.loads(data)
    for product in products["products"]:
        Product.create(**product)
