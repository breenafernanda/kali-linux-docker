import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import subprocess, os
import asyncio
import websockets
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

async def aguardar_elemento(driver, elemento):
        # Wait for the input field to be present
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, elemento))
        )
        return element
        
async def abrir_navegador(browser='chrome'):
    try:
        if browser.lower() == 'chrome':
            chrome_options = Options()
            
            # Set Chrome options for headless mode and no-sandbox
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration
            chrome_options.add_argument('--no-sandbox')   # Disable sandboxing for non-graphical environment
            chrome_options.add_argument('--disable-dev-shm-usage')  # Disable /dev/shm usage
            chrome_options.add_argument('--disable-software-rasterizer')  # Desativar rasterização de software
            chrome_options.add_argument('--disable-extensions')  # Desativar extensões

            # Set additional options as needed
            # chrome_options.add_argument('--some-option')
            capabilities = {
                    'browserName': 'chrome',
                    'goog:chromeOptions': {
                        'args': ['--headless', '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage', '--disable-software-rasterizer', '--disable-extensions'],
                        'log-level': 'DEBUG'
                    }
            }
            # driver = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities)
            # Initialize the Chrome WebDriver with the configured options
            driver = webdriver.Chrome(options=chrome_options)
            print('>>> WEBDRIVER INICIADO COM SUCESSO!')
            return driver
        else:
            print(f'Unsupported browser: {browser}')

    except Exception as e:
        print(f'ERRO AO ABRIR NAVEGADOR -> {e}')
        return f'Erro ao iniciar browser: {e}'

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

async def executar_no_terminal(comando):
    try:
        resultado = subprocess.run(comando, shell=True, check=True, capture_output=True, text=True)
        print(f"Comando recebido:\x1b[36m {comando}\n\n\x1b[34mComando executado com sucesso!\x1b[0m")
        print(f'\x1b[33msaída do terminal -> {resultado.stdout}\x1b[0m')
        return resultado.stdout
    except subprocess.CalledProcessError as e:
        print(f"\x1b[35mErro ao executar o comando:\n {e}\x1b[0m")
        return f"Erro ao executar o comando:\n {e}"

async def run_command(command: str):
    if command == 'config':
        try:
                # await executar_no_terminal('pip install pyppeteer')
                driver = await abrir_navegador(browser='chrome')
                driver.get('https://www.google.com.br')
                print(f'Acessou link do google')
                return f' ✅  Webdriver acessado com sucesso   ✅'
                
        except Exception as e: return f'❌ Erro ao acessar webdriver: {e}'
    else:
        retorno = await executar_no_terminal(command)
        print(f"Comando recebido: {command}")
        return f'Comando enviado:{command}\n\nComando Recebido pela API com sucesso ✅\n\n\n🤖 {retorno}\n_________________________________'

@app.get("/terminal", response_class=HTMLResponse)
async def terminal():
    return HTMLResponse(content=open("templates/terminal.html", "r").read(), status_code=200)

@app.post("/run_command")
async def execute_command(command: dict):
    try:
        result = await run_command(command['command'])
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/financiamento")
async def execute_command(json_data: dict):
    try:
        print(f'Json recebido: {json_data}')
        return {"result": json_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
