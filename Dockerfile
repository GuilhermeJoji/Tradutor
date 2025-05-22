FROM python:3.10-slim

# Instala pacotes do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    cmake \
    build-essential \
    pkg-config \
    && apt-get clean

# Define o diretório de trabalho
WORKDIR /app
COPY . /app

# Instala as dependências do Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expõe a porta usada pelo Streamlit
EXPOSE 8080

# Comando para iniciar o app
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.enableCORS=false"]
