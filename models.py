import peewee as p

db = p.SqliteDatabase('db.sqlite3')

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
    cvv = p.CharField()
    expiration_month = p.IntegerField()

class Transaction(BaseModel):
    id = p.CharField(primary_key=True)
    success = p.BooleanField(default=False)
    amount_charged = p.DoubleField()

class Order(BaseModel):
    id = p.AutoField(primary_key=True)
    total_price = p.DoubleField()
    email = p.CharField(null=True)
    credit_card = p.ForeignKeyField(Credit_Card,null=True)
    shipping_information = p.ForeignKeyField(Shipping_Information,null=True)
    paid = p.BooleanField(default=False)
    transaction = p.ForeignKeyField(Transaction,null=True)
    product = p.ForeignKeyField(Product)
    quantity = p.IntegerField()
    shipping_price = p.DoubleField()
