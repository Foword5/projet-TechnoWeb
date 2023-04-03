import os

os.environ['DB_HOST'] = 'localhost'
os.environ['DB_USER'] = 'user'
os.environ['DB_PASSWORD'] = 'pass'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'api8inf349'

os.environ['FLASK_DEBUG'] = 'True'
os.environ['FLASK_APP'] = 'api8inf349'
os.environ['REDIS_URL'] = 'redis://localhost'

#test les variables d'environnement

print("DB_HOST :", os.environ['DB_HOST'])
print("DB_USER :", os.environ['DB_USER'])
print("DB_PASSWORD :", os.environ['DB_PASSWORD'])
print("DB_PORT :", os.environ['DB_PORT'])
print("DB_NAME :", os.environ['DB_NAME'])
print("FLASK_DEBUG :", os.environ['FLASK_DEBUG'])
print("FLASK_APP :", os.environ['FLASK_APP'])
print("REDIS_URL :", os.environ['REDIS_URL'])