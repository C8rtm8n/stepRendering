# Použití základního Python image
FROM python:3.9-slim

# Nastavení pracovního adresáře
WORKDIR /app

# Kopírování požadavků
COPY requirements.txt /app/requirements.txt

# Instalace závislostí
RUN pip install --no-cache-dir -r requirements.txt

# Kopírování kódu aplikace
COPY . /app

# Exponování portu Streamlit
EXPOSE 8501

# Spuštění aplikace
CMD ["streamlit", "run", "stepRender.py", "--server.port=8501", "--server.address=0.0.0.0"]
