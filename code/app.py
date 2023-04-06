from flask import Flask, jsonify, request
from playhouse.shortcuts import model_to_dict
import urllib.request
from urllib.error import HTTPError
import json
from models import *
import redis
from rq import Queue, Worker, get_current_job

app = Flask(__name__)
REDIS_URL = os.environ.get('REDIS_URL')
redis_client = redis.from_url(REDIS_URL)

@app.route('/')
def products():
    products = {"products": []}
    for product in Product.select():
        products["products"].append(model_to_dict(product))
    return jsonify(products)

#get order
@app.route('/order/<int:id>', methods=['GET'])
def get_order(id):

    paymentQueue = Queue(name='payment', connection=redis_client, result_ttl=10)

    currendJob = paymentQueue.fetch_job(str(id))
    if currendJob != None and currendJob.is_finished == False:
        return "", 202

    order = redis_client.get(id)
    if order == None:
        try:
            order = Order.get(Order.id == id)
            #jsonify the order
            order = model_to_dict(order)
        except Order.DoesNotExist:
            return jsonify(
                { "errors" : 
                { "order": 
                { "code": "not-found", "name": "La commande demandée n'existe pas" } 
                    } 
                } ), 422
    else:
        order = json.loads(order)

    #if credit_card is null or shipping_information is null or transaction is null, replace null value with an empty object
    if order["credit_card"] == None:
        order["credit_card"] = {}
    if order["shipping_information"] == None:
        order["shipping_information"] = {}
    if order["transaction"] == None:
        order["transaction"] = {}

    #get all products ordered 
    products = []
    for productOrdered in ProductOrdered.select().where(ProductOrdered.order == order["id"]):
        product = model_to_dict(productOrdered)
        products.append(
            {
                "id": product["product"]["id"],
                "quantity": product["quantity"]
            }
        )
    #if there is only one product, we add a product field to the order
    if len(products) == 1:
        order["product"] = products[0]
    order["products"] = products

    return jsonify(order)
        
    
#create new order
@app.route('/order', methods=['POST'])
def create_order():

    #check if the body contains a product with an id and a quantity
    if "product" not in request.json and ("products" not in request.json or len(request.json["products"]) < 1):
        return jsonify(
            { "errors" : 
             { "product": 
              { "code": "missing-fields", "name": "La création d'une commande nécessite un produit" } 
                } 
            } ), 422
    
    #we create a liste containing either the one product or the list of products
    #we prioritize the list of products
    if "products" in request.json :
        products = request.json["products"]
    else:
        products = [request.json["product"]]
    
    #verify all possibles errors before creating the order
    for product in products:
        if "id" not in product or "quantity" not in product:
            return jsonify(
                { "errors" : 
                    { "product": 
                    { "code": "missing-fields", "name": "La création d'une commande nécessite un id et une quantité" } 
                    } 
                } ), 422
        #get the product if it exists
        if product["quantity"] < 1:
            return jsonify(
                { "errors" : 
                    { "product": 
                    { "code": "missing-fields", "name": "La quantité doit être supérieure ou égale à 1" } 
                    } 
                } ), 422
        try:
            product = Product.get(Product.id == product["id"])
        except Product.DoesNotExist:
            #if the product doesn't exist
            return jsonify(
                { "errors" : 
                    { "product": 
                    { "code": "not-found", "name": "L'un des produits demandé n'existe pas" } 
                    } 
                } ), 422
        if product.in_stock == False : #if the product is not in stock
            return jsonify(
                { "errors" : 
                    { "product": 
                    { "code": "out-of-inventory", "name": "L'un des produit demandé n'est pas en inventaire" } 
                    } 
                } ), 422

    #create the order
    order = Order.create()

    total_price = 0
    shippingWeight = 0

    for product in products:
        #get the product
        productObject = Product.get(Product.id == product["id"])
        #add the product to the order
        ProductOrdered.create(
            order = order,
            product = productObject,
            quantity = product["quantity"]
        )
        #add the price of the product to the shipping price
        total_price += productObject.price * product["quantity"]
        #add the weight of the product to the shipping weight
        shippingWeight += productObject.weight * product["quantity"]
    

    if shippingWeight < 500:
        shipping_price = total_price + 5
    elif shippingWeight < 2000:
        shipping_price = total_price + 10
    else:
        shipping_price = total_price + 25

    #adding the total price and the shipping price to the order
    (
        Order.update({"shipping_price": shipping_price, "total_price": total_price}) 
        .where(Order.id ==order.id)
        .execute()
    )

    return jsonify(model_to_dict(order)), 302, {'Location': '/order/' + str(order.id)}
    
        

@app.route('/order/<int:order_id>', methods=["PUT"])
def update_order(order_id):
    paymentQueue = Queue(name='payment', connection=redis_client, result_ttl=10)

    currendJob = paymentQueue.fetch_job(str(order_id))
    if currendJob != None and currendJob.is_finished == False:
        return jsonify({
            "errors" : {
                "order": {
                    "code": "in-process",
                    "name": "La commande est en cours de traitement.",
                    }
                }
            } ), 409
    try:
        order = Order.get(Order.id == order_id)
        #jsonify the order
        order = model_to_dict(order)

        #checking if there is both credit card and shippment
        if "order" in request.json and "credit_card" in request.json :
            return jsonify({
                "errors" : {
                    "order": {
                        "code": "missing-fields",
                        "name": "Vous ne pouvez ajouter les informations sur le client et sur la carte de crédit en même temps",
                        }
                    }
                } ), 422
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
            
            #creating the data to send to the payement API
            paymentData = {
                "credit_card" : creditCardInfo,
                "amount_charged": order["shipping_price"]
            }

            job = paymentQueue.enqueue(checkForPayement, paymentData, order_id, job_id=str(order_id))
            
            return "", 202
        
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
            } ), 404

#A function to check if the payement is accepted
def checkForPayement(creditCardInfo, order_id):
    try :
        #asking the payement API if the payement is accepted
        paymenent = urllib.request.urlopen("http://dimprojetu.uqac.ca/~jgnault/shops/pay/", data = json.dumps(creditCardInfo).encode('utf-8'))
        payementInfo = json.loads(paymenent.read().decode("utf-8"))

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
            .where(Order.id == order_id)
            .execute()
        )

        order = Order.get(Order.id == order_id)
        #jsonify the order
        order = model_to_dict(order)

        redis_client.set(order["id"], json.dumps(order))
    
    except HTTPError as e:
        #if the paymenet is refused, then we send the error
        payementInfo = json.loads(e.read())

        PaymentError.create(
            statusCode = e.code,
            code = payementInfo["errors"]["credit_card"]["code"]
        )

        error = Error.create(
            code = payementInfo["errors"]["credit_card"]["code"],
            name = payementInfo["errors"]["credit_card"]["name"]
        )

        transaction = Transaction.create(
            success = False,
            error = error
        )

        #add the error to the order
        (
            Order.update({"transaction":transaction})
            .where(Order.id == order_id)
            .execute()
        )
    

@app.cli.command("init-db") # s'exécute avec la commande flask init-db
def init_db():
    connection = redis.from_url(os.environ.get('REDIS_URL'))
    connection.flushdb()

    db.drop_tables([Product, Shipping_Information, Credit_Card, Transaction, Order, ProductOrdered, PaymentError, Error],cascade=True)
    db.create_tables([Product, Shipping_Information, Credit_Card, Transaction, Order, ProductOrdered, PaymentError, Error])

@app.cli.command("worker")
def worker():
    connection = redis.from_url(os.environ.get('REDIS_URL'))
    
    my_worker = Worker(queues=[Queue('payment', connection=connection, result_ttl=10)], connection=connection)
    my_worker.work()

@app.before_first_request # s'exécute entre le démarrage du serveur et le premier appel
def init_products():
    Product.delete().execute()
    try:
        data = urllib.request.urlopen("http://dimprojetu.uqac.ca/~jgnault/shops/products/products.json").read().decode("utf-8")
        products = json.loads(data)
        for product in products["products"]:
            # Supprimer les caractères nuls de chaque chaîne de caractères
            for key, value in product.items():
                if isinstance(value, str):
                    product[key] = value.replace('\x00', '')
            Product.create(**product)
    except HTTPError as e:
        # If we can't get the products
        error = json.loads(e.read())
        print(e.code, error)
