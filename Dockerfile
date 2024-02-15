# Imagem base do Kali Linux
FROM kalilinux/kali-rolling

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

EXPOSE $PORT
EXPOSE 5000
# Configurando as variáveis de ambiente para a execução do script Python
RUN echo $CREDENTIAL > /tmp/debug

# CMD para iniciar o seu script Python (substitua o comando abaixo pelo seu)
# CMD ["/usr/bin/python3", "/caminho/do/seu/script.py"]
