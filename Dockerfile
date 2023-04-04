# Utilise l'image officielle Python 3.9 comme base
FROM python:3.9-slim-buster

# Définit l'environnement de travail comme /app
WORKDIR /app

# Copie les fichiers requirements.txt dans l'image
COPY requirements.txt .

# Installe les dépendances spécifiées dans requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le code source dans l'image
COPY . /app

# Expose le port 5000 pour les connexions entrantes
EXPOSE 5000

CMD flask init-db && flask run



