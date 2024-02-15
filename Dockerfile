# Estágio 1: Configuração do Kali Linux e Google Chrome
FROM kalilinux/kali-rolling as kali

# Atualiza os repositórios e instalações necessárias
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get -y install wget gnupg xorg xauth

# Adiciona o repositório do Google Chrome e instala o navegador
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/google-chrome-archive-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list > /dev/null && \
    apt-get update && \
    apt-get -y install google-chrome-stable

# Configuração para evitar erros com o D-Bus
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null

# Descobre o IP público do contêiner e imprime para o log
RUN apt-get -y install curl

# Configurando as variáveis de ambiente para a execução do script Python
RUN echo "IP público do docker: \$(curl -s ifconfig.me)" > /tmp/ip_info && \
    echo "Porta exposta: 8000" >> /tmp/ip_info

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
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install uvicorn fastapi

# Copiar o código-fonte para o contêiner
COPY . /app/

# Expor a porta que a aplicação FastAPI estará escutando
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["sh", "-c", "cat /tmp/ip_info && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]
