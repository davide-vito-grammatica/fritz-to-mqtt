# Usa un'immagine base di Python
FROM python:3.9-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file di configurazione nella directory di lavoro
COPY requirements.txt .

RUN pip install --upgrade pip
# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt


# Comando per eseguire l'applicazione
CMD ["python", "src/main.py"]