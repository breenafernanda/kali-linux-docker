# Use a imagem base do Python
FROM python:3.9

# Configure o ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Crie e configure o diretório de trabalho
WORKDIR /app

# Copie o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt /app/

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o conteúdo do diretório atual para o diretório de trabalho
COPY . /app/

# Exponha a porta 5000 (ou a porta que você estiver usando)
EXPOSE 5000

# Comando para executar sua aplicação Flask
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "API:app"]
