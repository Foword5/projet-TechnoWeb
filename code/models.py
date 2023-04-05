import peewee as p
import datetime
import os

DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')


db = p.PostgresqlDatabase(
    DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

class BaseModel(p.Model):
    class Meta:
        database = db

class Product(BaseModel):
    name = p.CharField()
    type = p.CharField()
    id = p.IntegerField(primary_key=True)
    in_stock = p.BooleanField(default=True)
    description = p.TextField()
    price = p.DoubleField()
    height = p.IntegerField()
    weight = p.IntegerField()
    image = p.CharField() 

class Shipping_Information(BaseModel):
    id = p.AutoField(primary_key=True)
    country = p.CharField()
    address = p.CharField()
    postal_code = p.CharField()
    city = p.CharField()
    province = p.CharField()

class Credit_Card(BaseModel):
    id = p.AutoField(primary_key=True)
    name = p.CharField()
    first_digits = p.CharField()
    last_digits = p.CharField()  
    expiration_year = p.IntegerField()
    expiration_month = p.IntegerField()

class Error(BaseModel):
    id = p.AutoField(primary_key=True)
    code = p.CharField()
    name = p.CharField()

class Transaction(BaseModel):
    true_id = p.AutoField(primary_key=True)
    id = p.CharField(null=True)
    success = p.BooleanField(default=False)
    amount_charged = p.DoubleField(null=True)
    error = p.ForeignKeyField(Error,null=True)

class Order(BaseModel):
    id = p.AutoField(primary_key=True)
    total_price = p.DoubleField(null=True)
    email = p.CharField(null=True)
    credit_card = p.ForeignKeyField(Credit_Card,null=True)
    shipping_information = p.ForeignKeyField(Shipping_Information,null=True)
    paid = p.BooleanField(default=False)
    transaction = p.ForeignKeyField(Transaction,null=True)
    shipping_price = p.DoubleField(null=True)

class ProductOrdered(BaseModel):
    product = p.ForeignKeyField(Product)
    order = p.ForeignKeyField(Order)
    quantity = p.IntegerField()

class PaymentError(BaseModel):
    id = p.AutoField(primary_key=True)
    statusCode = p.CharField()
    code = p.CharField()
    time = p.DateTimeField(default=datetime.datetime.now)
