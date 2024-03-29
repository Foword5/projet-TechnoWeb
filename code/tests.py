import pytest
from app import *
import time

# Create a test client using the Flask application configured for testing

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client

def test_index(client):
    #getting all the products
    rv = client.get('/')
    assert rv.status_code == 200 


def test_create_order(client):
    #creating a new order successfully
    rv = client.post('/order', json={
        "product": { "id": 2, "quantity": 2 }
    })
    assert rv.status_code == 302

    #unknown product
    rv = client.post('/order', json={
        "product": { "id": 123, "quantity": 2 }
    })
    assert rv.status_code == 422

    #missing field
    rv = client.post('/order', json={
        "product": {"quantity": 2 }
    })
    assert rv.status_code == 422

    #quantity < 1
    rv = client.post('/order', json={
        "product": { "id": 123, "quantity": 0 }
    })
    assert rv.status_code == 422

    #product out of stock
    rv = client.post('/order', json={
        "product": { "id": 4, "quantity": 2 }
    })
    assert rv.status_code == 422

    #created from list
    rv = client.post('/order', json={ 
        "products":[
            {
                "id": 2,
                "quantity": 2
            },
            {
                "id": 3,
                "quantity": 2
            } 
        ]
    })
    assert rv.status_code == 302

    #created from list with one product out of stock
    rv = client.post('/order', json={ 
        "products":[
            {
                "id": 2,
                "quantity": 2
            },
            {
                "id": 4,
                "quantity": 2
            } 
        ]
    })
    assert rv.status_code == 422

    #created from list with one product unknown
    rv = client.post('/order', json={ 
        "products":[
            {
                "id": 456,
                "quantity": 2
            },
            {
                "id": 3,
                "quantity": 2
            } 
        ]
    })
    assert rv.status_code == 422

    #empty list
    rv = client.post('/order', json={ 
        "products":[]
    })
    assert rv.status_code == 422

    #no json
    rv = client.post('/order')
    assert rv.status_code == 400

def test_get_order(client):
    #get order successfully
    rv = client.get('/order/1')
    assert rv.status_code == 200 and rv.json['id'] == 1

    #inexisting order
    rv = client.get('/order/123')
    assert rv.status_code == 422

    #no order id specified
    rv = client.get('/order/')
    assert rv.status_code == 404

def test_put_order(client):
    #we create multiple orders to test the put method
    client.post('/order', json={
        "product": { "id": 2, "quantity": 2 }
    })
    client.post('/order', json={
        "product": { "id": 2, "quantity": 2 }
    })
    #and we add the shipping info
    client.put('/order/2', json={
        "order" : {
            "email" : "jgnault@uqac.ca",
            "shipping_information" : {
                "country" : "Canada",
                "address" : "201, rue Président-Kennedy",
                "postal_code" : "G7X 3Y7",
                "city" : "Chicoutimi",
                "province" : "QC"
                }
        }
    })
    client.put('/order/3', json={
        "order" : {
            "email" : "jgnault@uqac.ca",
            "shipping_information" : {
                "country" : "Canada",
                "address" : "201, rue Président-Kennedy",
                "postal_code" : "G7X 3Y7",
                "city" : "Chicoutimi",
                "province" : "QC"
                }
        }
    })

    #no json
    rv = client.put('/order/1')
    assert rv.status_code == 400

    #Order not found
    rv = client.put('/order/100000', json={
        "order" : {
            "email" : "jgnault@uqac.ca",
            "shipping_information" : {
                "country" : "Canada",
                "address" : "201, rue Président-Kennedy",
                "postal_code" : "G7X 3Y7",
                "city" : "Chicoutimi",
                "province" : "QC"
                }
        }
    })
    assert rv.status_code == 404

    #empty json
    rv = client.put('/order/1', json={
    })
    assert rv.status_code == 422

    #both credit card info and shippement info at the same time
    rv = client.put('/order/1', json={
        "credit_card" : {
            "name" : "John Doe",
            "number" : "4242 4242 4242 4242",
            "expiration_year" : 2024,
            "cvv" : "123",
            "expiration_month" : 9
        },
        "order" : {
            "email" : "jgnault@uqac.ca",
            "shipping_information" : {
                "country" : "Canada",
                "address" : "201, rue Président-Kennedy",
                "postal_code" : "G7X 3Y7",
                "city" : "Chicoutimi"
                }
        }
    })
    assert rv.status_code == 422

    #adding credit card info before shippement info
    rv = client.put('/order/1', json={
        "credit_card" : {
            "name" : "John Doe",
            "number" : "4242 4242 4242 4242",
            "expiration_year" : 2024,
            "cvv" : "123",
            "expiration_month" : 9
        }
    })
    assert rv.status_code == 422

    #missing either order or creadit card field
    rv = client.put('/order/1', json={})
    assert rv.status_code == 422

    #missing field in shippement info
    rv = client.put('/order/1', json={
        "order" : {
            "email" : "jgnault@uqac.ca",
            "shipping_information" : {
                "country" : "Canada",
                "address" : "201, rue Président-Kennedy",
                "postal_code" : "G7X 3Y7",
                "city" : "Chicoutimi"
                }
        }
    })
    assert rv.status_code == 422

    #Adding shippement info successfully
    rv = client.put('/order/1', json={
        "order" : {
            "email" : "jgnault@uqac.ca",
            "shipping_information" : {
                "country" : "Canada",
                "address" : "201, rue Président-Kennedy",
                "postal_code" : "G7X 3Y7",
                "city" : "Chicoutimi",
                "province" : "QC"
                }
        }
    })
    assert rv.status_code == 200

    #missing credit card info
    rv = client.put('/order/1', json={
        "credit_card" : {
            "name" : "John Doe",
            "number" : "4242 4242 4242 4242",
            "expiration_year" : 2024,
            "cvv" : "123"
        }
    })
    assert rv.status_code == 422

    #card refused
    rv = client.put('/order/1', json={
        "credit_card" : {
            "name" : "John Doe",
            "number" : "4000 0000 0000 0002",
            "expiration_year" : 2024,
            "cvv" : "123",
            "expiration_month" : 9
        }
    })
    assert rv.status_code == 202

    #unknown card
    rv = client.put('/order/2', json={
        "credit_card" : {
            "name" : "John Doe",
            "number" : "4000 5735 2356 4502",
            "expiration_year" : 2024,
            "cvv" : "123",
            "expiration_month" : 9
        }
    })
    assert rv.status_code == 202

    #successfully adding credit card info and paying
    rv = client.put('/order/3', json={
        "credit_card" : {
            "name" : "John Doe",
            "number" : "4242 4242 4242 4242",
            "expiration_year" : 2024,
            "cvv" : "123",
            "expiration_month" : 9
        }
    })
    assert rv.status_code == 202

    #Order being treated
    rv = client.put('/order/3', json={
        "credit_card" : {
            "name" : "John Doe",
            "number" : "4242 4242 4242 4242",
            "expiration_year" : 2024,
            "cvv" : "123",
            "expiration_month" : 9
        }
    })
    assert rv.status_code == 409
    