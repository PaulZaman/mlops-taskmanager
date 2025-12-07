# Image Python légère
FROM python:3.12-slim

# Répertoire de travail dans le container
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier 
COPY . .

EXPOSE 5001

# Commande de démarrage en production
CMD ["python", "app.py"]