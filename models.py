import peewee as p

db = p.SqliteDatabase('db.sqlite')

class BaseModel(p.Model):
    class Meta:
        database = db


class Product(BaseModel):
    name = p.CharField()
    id = p.AutoField(primary_key=True)
    in_stock = p.BooleanField(default=True)
    description = p.TextField()
    price = p.DecimalField(max_digits=10, decimal_places=2)
    weight = p.DecimalField(max_digits=10, decimal_places=2)
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
    number = p.CharField()
    expiration_year = p.IntegerField()
    cvv = p.CharField()
    expiration_month = p.IntegerField()

class Transaction(BaseModel):
    id = p.CharField(primary_key=True)
    success = p.BooleanField(default=False)
    amount_charged = p.DecimalField(max_digits=10, decimal_places=2)

class Order(BaseModel):
    id = p.AutoField(primary_key=True)
    total_price = p.DecimalField(max_digits=10, decimal_places=2)
    email = p.CharField(default='null')
    credit_card = p.ForeignKeyField(Credit_Card, related_name='orders')
    shipping_information = p.ForeignKeyField(Shipping_Information, related_name='orders')
    paid = p.BooleanField(default=False)
    transaction = p.CharField()
    product = p.ForeignKeyField(Product, related_name='orders')
    quantity = p.IntegerField()
    shipping_price = p.DecimalField(max_digits=10, decimal_places=2)
