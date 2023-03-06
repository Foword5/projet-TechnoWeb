# PROJET TECHNOLOGIES WEB AVANCÉES
### Lelièvre David, Delamare Jules
<br />

## Run App
Initialiser la base de données : <br />
Initialise database :
```sh
FLASK_DEBUG=True FLASK_APP=inf349 flask init-db 
```

Lancer l'application :<br />
Run the app :
```sh
FLASK_DEBUG=True FLASK_APP=inf349 flask run
```

## Run Test 
Bien penser à réinitialiser la base de donnée :<br />
Don't forget to reset the database before testing :
```sh
FLASK_DEBUG=True FLASK_APP=inf349 flask init-db 
```

Lancer les tests :<br />
Run tests :
```sh
pytest -v tests.py
```
