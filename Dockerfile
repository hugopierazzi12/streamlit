# Utiliser une image Python comme base
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copier tout le code de l'application
COPY . .

# Exposer le port 8501
EXPOSE 8501

# Démarrer l'application Streamlit
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.enableCORS=false"]
