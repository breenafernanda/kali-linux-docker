FROM kalilinux/kali-rolling

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get -y install wget gnupg

# Adiciona o repositório do Google Chrome e instala o navegador
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/google-chrome-archive-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list > /dev/null && \
    apt-get update && \
    apt-get -y install google-chrome-stable

RUN wget -qO /bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.3/ttyd.x86_64 && \
    chmod +x /bin/ttyd

EXPOSE $PORT
RUN echo $CREDENTIAL > /tmp/debug

# CMD ["/bin/bash", "-c", "/bin/ttyd -p $PORT -c $USERNAME:$PASSWORD /usr/bin/google-chrome-stable"]

# CMD sem autenticação (comentado para referência)
CMD ["/bin/bash", "-c", "/bin/ttyd -p $PORT /usr/bin/google-chrome-stable"]
