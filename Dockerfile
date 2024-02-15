# Estágio 1: Configuração do Kali Linux e Google Chrome
# FROM kalilinux/kali-rolling as kali
FROM debian:buster-slim
# Atualiza os repositórios e instalações necessárias
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get -y install wget gnupg xorg xauth

# Adiciona o repositório do Google Chrome e instala o navegador
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/google-chrome-archive-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list > /dev/null && \
    apt-get update && \
    apt-get -y install google-chrome-stable
ENV PATH="/path/to/chrome/directory:$PATH"

# Configuração para evitar erros com o D-Bus
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null

# Descobre o IP público do contêiner e imprime para o log
RUN apt-get -y install curl jq

# Configuração do Google Chrome para execução headless e no-sandbox
RUN apt-get -y install libnss3-tools
RUN groupadd -r chrome && useradd -r -g chrome -G audio,video chrome && \
    mkdir -p /home/chrome && chown -R chrome:chrome /home/chrome
RUN sed -i 's|HERE/chrome\"|HERE/chrome\" --headless --disable-gpu --no-sandbox|g' /usr/bin/google-chrome

# Configurando as variáveis de ambiente para a execução do script Python
RUN echo $CREDENTIAL > /tmp/debug

# Estágio 2: Configuração da aplicação FastAPI
FROM python:3.9

# Configurar variáveis de ambiente
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Criar e definir o diretório de trabalho
WORKDIR /app

# Copiar os requisitos do projeto para o contêiner
COPY requirements.txt /app/

# Instalar as dependências
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uvicorn fastapi  # Adicionando a instalação do FastAPI

# Criação de um ambiente virtual
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copiar o código-fonte para o contêiner
COPY . /app/

# Instalar o pydantic_settings
RUN pip install pydantic-settings

# Instalar o psycopg2 para PostgreSQL
RUN pip install psycopg2-binary

# Instalar as dependencias necessárias
RUN pip install uvicorn aiofiles
RUN pip install fastapi
RUN pip install selenium
RUN pip install webdriver-manager
RUN pip install websockets

# Expor a porta que a aplicação FastAPI estará escutando
EXPOSE 8000

RUN export PUBLIC_IP=$(curl -s https://httpbin.org/ip | jq -r .origin) && \
    echo "IP público do contêiner: ${PUBLIC_IP} e Porta exposta: 8000"
RUN google-chrome-stable --version || echo "Google Chrome não está instalado corretamente!"

# Comando para iniciar a aplicação
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]
