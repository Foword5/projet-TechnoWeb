# PROJET TECHNOLOGIES WEB AVANCÉES
### Lelièvre David, Delamare Jules
<br />

## Run App Locally

Prérequis :<br />
Prerequisites :
- Python 3.6
- PostgreSQL (avec un utilisateur "user", un mot de passe "pass" et une base de données "api8inf349", le tout sur le port 5432)
- Redis (sur le port 6379)

Installer les dépendances :<br />
Install dependencies :
```sh
pip install -r requirements.txt
```
Definir les variables d'environnement (sous linux) :<br />
Set environment variables :
```sh
export FLASK_APP=api8inf349
export FLASK_DEBUG=True
export REDIS_URL=redis://localhost
export DB_HOST=localhost
export DB_USER=user
export DB_PASSWORD=pass
export DB_NAME=api8inf349
export DB_PORT=5432
```
Definir les variables d'environnement (sous windows) :<br />
Set environment variables :
```sh
set FLASK_APP=api8inf349
set FLASK_DEBUG=True
set REDIS_URL=redis://localhost
set DB_HOST=localhost
set DB_USER=user
set DB_PASSWORD=pass
set DB_NAME=api8inf349
set DB_PORT=5432
```

Initialiser la base de données : <br />
Initialise database :
```sh
flask init-db 
```

Lancer le gestionnaire de tâches :<br />
Run the task server :
```sh
flask worker
```
Lancer l'application :<br />
Run the app :
```sh
flask run
```
## Run Test 
Bien penser à réinitialiser la base de donnée :<br />
Don't forget to reset the database before testing :
```sh
flask init-db 
```

Lancer les tests :<br />
Run tests :
```sh
pytest -v tests.py
```

## Run App with Docker
Prérequis :<br />
Prerequisites :
- Docker

Lancer les services :<br />
Run services :
```sh
docker-compose up
```
Lancer l'application :<br />
Run the app :
```sh
docker build -t api8inf349 .
docker run -e REDIS_URL=redis://host.docker.internal -e DB_HOST=host.docker.internal -e DB_USER=user -e DB_PASSWORD=pass -e DB_NAME=api8inf349 -e DB_PORT=5432 -p 5000:5000 api8inf349
```
```

