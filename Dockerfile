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

# Instala o ttyd para expor a interface gráfica
RUN wget -qO /bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.3/ttyd.x86_64 && \
    chmod +x /bin/ttyd

# Expondo a porta para o ttyd
EXPOSE $PORT

# Configurando as variáveis de ambiente para a execução do ttyd
RUN echo $CREDENTIAL > /tmp/debug

# Adiciona a configuração para iniciar o ttyd com o Chrome headless e no-sandbox
CMD ["/bin/bash", "-c", "\
    # Configuração para evitar erros com o D-Bus\
    export DBUS_SESSION_BUS_ADDRESS=/dev/null && \
    # Início do ttyd com o Chrome headless e no-sandbox\
    /bin/ttyd -p $PORT /usr/bin/google-chrome-stable --no-sandbox --headless\
"]
