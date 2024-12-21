# Použití základního image s podporou conda
FROM continuumio/miniconda3:latest

# Nastavení pracovního adresáře
WORKDIR /app

# Kopírování požadavků a kódu aplikace
COPY environment.yml /app/environment.yml
COPY . /app

# Instalace závislostí pomocí conda s retry mechanismem
RUN conda env create -f environment.yml --quiet || conda env create -f environment.yml --quiet || conda env create -f environment.yml --quiet && conda clean -afy

# Aktivace conda prostředí
SHELL ["conda", "run", "-n", "steprendering_env", "/bin/bash", "-c"]

# Exponování portu pro Streamlit
EXPOSE 8501

# Spuštění aplikace
CMD ["streamlit", "run", "stepRender.py", "--server.port=8501", "--server.address=0.0.0.0"]
