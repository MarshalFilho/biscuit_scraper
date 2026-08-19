FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copia arquivo de dependências e instala
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install flask google-generativeai

# Copia todo o código-fonte
COPY . .

# Expõe a porta 8080 exigida pelo Google Cloud Run
EXPOSE 8080

CMD ["python", "src/cloud_server.py"]
