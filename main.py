from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import subprocess, os, asyncio, websockets, time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


async def aguardar_elemento(driver, tempo, tipo, code):
    try:
        if tipo == 'CSS':   
            element = WebDriverWait(driver, tempo).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, code))
            )
        elif tipo == 'ID':
            element = WebDriverWait(driver, tempo).until(
                EC.element_to_be_clickable((By.ID, code))
            )  
        return element
    except Exception as e:  
        # print(f'\x1b[36m erro ao aguardar elemento {e}\x1b[0m')
        return 'Elemento não encontrado'
        
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
            # Initialize the Chrome WebDriver with the configured options
            try: # dessa forma executa em conteiner (railway)
                driver = webdriver.Chrome(options=chrome_options)
                    
            except Exception as e:  # dessa forma pode ser acessado via localhost (otimização de tempo de teste)
                driver_manager = ChromeDriverManager()
                driver = webdriver.Chrome(executable_path=driver_manager.install(), options=options)
            print('\x1b[34m>>> 🌐   WEBDRIVER INICIADO COM SUCESSO! <<<\x1b[0m')
            return driver

        else:
            print(f'Unsupported browser: {browser}')

    except Exception as e:
        print(f'ERRO AO ABRIR NAVEGADOR -> {e}')
        return f'Erro ao iniciar browser: {e}'

async def acessar_santander(driver, cliente):

    numero_proposta = '{TESTE RAILWAY}'
    for i in range(0,5): # relogar 3 vezes (BUG SANTANDER)
        try:
            url = 'https://brpioneer.accenture.com/originacao-loj/identification'
            driver.get(url)
            ## deslogar e logar novamente para resolver bug dos termos e condições
            try:
                # expandir menu {  v  }
                setinha_baixo = await aguardar_elemento(driver, 10, 'CSS', 'body > app-root > app-header > app-header-shopkeeper > div.desktop.d-none.d-md-block > mat-toolbar > span.user-menu.step9 > i')
                driver.execute_script("arguments[0].click();", setinha_baixo)

                # clicar em sair
                botao_sair = driver.find_element(By.CSS_SELECTOR,'body > app-root > app-header > app-header-shopkeeper > div.desktop.d-none.d-md-block > mat-toolbar > app-menu-profile > mat-card > mat-card-content > mat-list > mat-list-item.mat-list-item.mat-focus-indicator.list-item-image > span > span.mat-ripple.mat-list-item-ripple')
                driver.execute_script("arguments[0].click();", botao_sair)

                botao_sim_sair_da_conta = await aguardar_elemento(driver, 5, 'CSS', '#mat-dialog-0 > app-exit-page > div:nth-child(4) > div:nth-child(2) > button')
                driver.execute_script("arguments[0].click();", botao_sim_sair_da_conta)
                

                try:
                    botao_gd_sair = await aguardar_elemento(driver,5,'CSS','#modal-cancel-button')
                    botao_gd_sair.click()
                except: pass
                    
                    
                print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   \x1b[34m🔒>>>> Logout realizado!\x1b[0m')

                inserir_cpf = await aguardar_elemento(driver,5,'ID', 'mat-input-0')
                inserir_cpf.send_keys('39291935824')
                inserir_senha = driver.find_element(By.ID, 'mat-input-1').send_keys('@Kinsol*23')
                botao_login = await aguardar_elemento(driver,5,'CSS', 'body > app-root > div > app-login-container > div > app-sign-in-container > div > div.content-container.mt-md-5.align-items-center.justify-content-center.d-flex > div > div > form > div:nth-child(8) > button')
                driver.execute_script("arguments[0].click();", botao_login)

                print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   \x1b[34m🔓>>>> Login realizado novamente!\x1b[0m')
            except Exception as e: 
                print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   \x1b[36m>>>>   ERRO EM DESLOGAR E LOGAR:\n\x1b[32m{e}\x1b[0m')
                return False
        except Exception as e: print(f'Erro ao relogar {e}')
        print(f'loop {i}')

    try:
        select = await aguardar_elemento(driver, 10, 'ID', 'mat-select-value-3').find_element(By.XPATH, './/span')
        select.click()
        print('>>> Clicou no campo de seleção <<<')
        cdc_option = await aguardar_elemento(driver, 5, 'CSS', '#mat-option-4 > span')
        driver.execute_script("arguments[0].click();", cdc_option)
        print('>>> Selecionou a opção CDC <<<')

    except Exception as e:
        print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   Erro ao clicar no select por id: {e}')
    try: # input cpf
        cpf_input = await aguardar_elemento(driver,10,'ID','mat-input-2')
        cpf_input.send_keys(cliente['cpf'])
    except Exception as e: pass
    try: # input nascimento
        nasc_input = driver.find_element(By.ID, 'mat-input-3')
        nasc_input.send_keys(cliente['nasc'])
    except Exception as e: pass
    try: # input telefone
        tel_input = driver.find_element(By.ID, 'mat-input-4')
        tel_input.send_keys('34997741385')
    except Exception as e: pass
    try: # input valor da proposta
        proposta_input = driver.find_element(By.ID, 'mat-input-5')
        valor_proposta = cliente['valor_proposta']
        if ',' in valor_proposta or '.' in valor_proposta:
            # Se houver vírgula ou ponto, remover a vírgula (a página entende os decimais)
            valor_proposta = valor_proposta.replace(',', '').replace('.', '')
        else:
            # Se for um número inteiro, adicionar dois zeros no final
            valor_proposta += '00'

        proposta_input.send_keys(int(valor_proposta))
    except Exception as e: pass
    try: # selecionar checkbox
        # definir elemento 
        box_termos_e_condicoes = await aguardar_elemento(driver,10,'CSS', 'body > app-root > div > app-identification > div > div.ng-star-inserted > div:nth-child(2) > app-terms-and-conditions > div.col-12.terms > p')
        # clicar no elemento para selecionar (é necessário?)
        driver.execute_script("arguments[0].click();", box_termos_e_condicoes)
        
        # Dar scroll até o final da caixa
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", box_termos_e_condicoes)
        checkbox_confirm = await aguardar_elemento(driver,5,'CSS','#mat-checkbox-2 > label > span.mat-checkbox-inner-container')
        await asyncio.sleep(2)
        driver.execute_script("arguments[0].click();", checkbox_confirm)
        print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0   ✅  Clicou em Confirmo que li e aceito os termos e condições!')
    except Exception as e: print(e)
    try: # preencher checkbox (circulos)
        circle1 = driver.execute_script("arguments[0].click();", driver.find_element(By.ID, 'mat-radio-3-input'))
        circle2 = driver.execute_script("arguments[0].click();", driver.find_element(By.ID, 'mat-radio-6-input'))
        circle3 = driver.execute_script("arguments[0].click();", driver.find_element(By.ID, 'mat-radio-9-input'))
    except Exception as e:
        print(f'\x1b[32m[ {numero_proposta} ]\x1b[0m   Erro ao clicar nos circles')
    # clicar em Buscar Ofertas
    try:
        
        buscar_ofertas = await aguardar_elemento(driver,10,'CSS', 'body > app-root > div > app-identification > div > div.row.identification-submit > div > button')
        await asyncio.sleep(2)
        buscar_ofertas.click()  
        print('>> CLicou no botão Buscar Ofertas <<<<')
    except Exception as e: 
            print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   erro ao clicar no botão Buscar Ofertas')
            try:
                elemento = await aguardar_elemento(driver, 10, 'CSS', 'body > app-root > div > app-identification > div > div.row.identification-submit > div > button')
                clicar =  driver.execute_script("arguments[0].click();", elemento)
                print('>>> Clicou em Buscar Ofertas <<<')
            except Exception as e: print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   erro ao clicar no botão buscar ofertas {e}')


    try: # obter valor das parcelas
        valor_parcela = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'body > app-root > div > app-step-offers-container > app-step-offers-npp > div > div > div.col.offset-md-4.col-md-8.content > div > div.ng-star-inserted > app-step-offer-npp > div:nth-child(2) > div.card-body > div.financied-value > p.financied-total.ng-star-inserted'))
        )
        qtde_parcelas = driver.find_element(By.CSS_SELECTOR, 'body > app-root > div > app-step-offers-container > app-step-offers-npp > div > div > div.col.offset-md-4.col-md-8.content > div > div.ng-star-inserted > app-step-offer-npp > div:nth-child(2) > div.card-body > div.financied-value > p.card-text.ng-star-inserted').text
        qtde_parcelas = qtde_parcelas.split(' ')
        qtde_parcelas = qtde_parcelas[0]

        valor_seguro_parcela = driver.find_element(By.CSS_SELECTOR, 'body > app-root > div > app-step-offers-container > app-step-offers-npp > div > div > div.col.offset-md-4.col-md-8.content > div > div.ng-star-inserted > app-step-offer-npp > div:nth-child(2) > div.card-body > div.insurance-value.ng-star-inserted > p.card-text').text
        valor_seguro_parcela = valor_seguro_parcela.split(' ')
        valor_seguro_parcela = valor_seguro_parcela[2]
                                    
        valor_com_seguro_total = driver.find_element(By.CSS_SELECTOR, 'body > app-root > div > app-step-offers-container > app-step-offers-npp > div > div > div.col.offset-md-4.col-md-8.content > div > div.ng-star-inserted > app-step-offer-npp > div:nth-child(2) > div.card-body > div.insurance-value.ng-star-inserted > p:nth-child(3) > span').text
        valor_com_seguro_total = valor_com_seguro_total.split(' ')
        valor_com_seguro_total = valor_com_seguro_total[1]
                             
    except Exception as e: print(f'\x1b[32m[ {numero_proposta} ]\x1b[0m   Elemento não encontrado: {e}')

    dados = {
                             'valor_parcela': valor_parcela.text,
                             'qtde_parcelas': qtde_parcelas,
                             'valor_seguro_parcela':valor_seguro_parcela,
                             'valor_com_seguro_total':valor_com_seguro_total
                        }
    return dados

async def acessar_bv(driver, cliente):
    numero_proposta = '{TESTE RAILWAY}'

    try:
        print(f'>>> Acessando banco BV <<<')
        url = 'https://instalador.meufinanciamentosolar.com.br/dashboard/home'
        driver.get(url)
        await asyncio.sleep(3)
        
    
        try: 
            print(f'URL ATUAL [login] >>> \n{driver.title}\n>>>{driver.current_url}\n\n')
            driver.find_element(By.ID, 'email').send_keys('sac@kinsolenergia.com.br')
            driver.find_element(By.ID, 'password').send_keys('BA8jkFeY*')
            driver.find_element(By.ID, 'login-form_button').click()
            await asyncio.sleep(3)
            print(f'>>> Realizando login no banco BV <<<')
        except Exception as e: print(f'\x1b[32m[ {numero_proposta} - BANCO BV ]\x1b[0m  {e} \x1b[33m>>><<<<')
        # VERIFICAR SE LOGOU COM SUCESSO! 
        print(f'URL ATUAL [dashboard] >>> \n{driver.title}\n>>>{driver.current_url}\n\n')
        
        try:
            driver.get('https://instalador.meufinanciamentosolar.com.br/dashboard/proposals-create')
            await asyncio.sleep(2)
            print(f'URL ATUAL[proposals-create] >>> \n{driver.title}\n>>>{driver.current_url}\n\n')

            cnpj_instalador = await aguardar_elemento(driver, 10, 'ID', 'installer_info_cnpj')
            if cnpj_instalador:
                cnpj_instalador.send_keys('18.902.786/0001-06')
            else:
                print("Elemento 'installer_info_cnpj' não encontrado.")
            driver.find_element(By.ID, 'installer_info_email').send_keys('camilacaetano.kinsol@gmail.com')
            driver.find_element(By.ID, 'value').clear()
            valor_proposta = cliente['valor_proposta']
            if ',' in valor_proposta:
                    valor_proposta = valor_proposta.split(',')[0]

            elif  '.' in valor_proposta:
                    # Se houver vírgula ou ponto, remover a vírgula (a página entende os decimais)
                    valor_proposta = valor_proposta.split('.')[0]
                    # valor_proposta = valor_proposta.replace(',', '').replace('.', '')

            driver.find_element(By.ID, 'value').send_keys(valor_proposta)

            driver.find_element(By.ID, 'name').send_keys(cliente['nome'])
            driver.find_element(By.ID, 'cnpj_cpf').send_keys(cliente['cpf'])
            driver.find_element(By.ID, 'postalcode').send_keys(cliente['cep'])
            driver.find_element(By.ID, 'birthdate').send_keys(cliente['nasc'])

            driver.find_element(By.CSS_SELECTOR, '#app-container > main > div > div > div > div > form > div:nth-child(8) > button').click()
            await asyncio.sleep(10)
            try:
                parcela1 = driver.find_element(By.CSS_SELECTOR, '#installmentsButtons > div:nth-child(1) > button').text
                parcela2 = driver.find_element(By.CSS_SELECTOR, '#installmentsButtons > div:nth-child(2) > button').text
                parcela3 = driver.find_element(By.CSS_SELECTOR, '#installmentsButtons > div:nth-child(3) > button').text
                parcela4 = driver.find_element(By.CSS_SELECTOR, '#installmentsButtons > div:nth-child(4) > button').text
                parcela5 = driver.find_element(By.CSS_SELECTOR, '#installmentsButtons > div:nth-child(5) > button').text
                parcela6 = driver.find_element(By.CSS_SELECTOR, '#installmentsButtons > div:nth-child(6) > button').text
                total_financiado_bv = driver.find_element(By.CSS_SELECTOR, '#app-container > main > div > div > div > div > form > p.resultsFinancedValue > strong').text
                # driver.find_element(By.CSS_SELECTOR, '#app-container > main > div > div > div > div > header > div:nth-child(1) > h1').send_keys(Keys.PAGE_DOWN)

                driver.execute_script("window.scrollBy(0, 400);")
                print(f'\x1b[32m[ {numero_proposta} - BANCO BV ]\x1b[33m Valor da parcela  {parcela1}\x1b[0m')
                parcelamento = {
                    'parcelamento1': parcela1,
                    'parcelamento2': parcela2,
                    'parcelamento3': parcela3,
                    'parcelamento4': parcela4,
                    'parcelamento5': parcela5,
                    'parcelamento6': parcela6,
                    'total_financiado': total_financiado_bv
                }
            except Exception as e:
                try:
                    
                    modal = driver.find_element(By.CSS_SELECTOR, '#myModal > div > div.modal-body-initial').text
                except:    pass
        except Exception as e: 
            print(f'\x1b[32m[ {numero_proposta} - BANCO BV ]\x1b[0m   \x1b[33m>>>Erro ao editar banco bv\x1b[0m<<<<{e}')
            parcelamento = None

        # Salvar a captura de tela
        
        return parcelamento
    except Exception as e: print(f'>>> Erro ao acessar banco BV \n{e}')
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
    cliente = {
                    'nome': 'Gabriel Graton Marcelo', 
                    'numero_proposta': 'K123456789.1',
                    'cpf': '39291935824', 
                    'nasc': '30/03/1992',
                    'cep': '38010-010',
                    'valor_proposta':'10000'
                }
    if command == 'santander': # executar roteiro do santander
        try:
                
                driver = await abrir_navegador(browser='chrome')
                print(f' ✅🌐  Webdriver acessado com sucesso   ✅ ')
                santander_status = await acessar_santander(driver, cliente)
                print(f' ✅🏦  Santander automatizado com sucesso   ✅ \n{santander_status}')
                return f' ✅🏦  Santander automatizado com sucesso   ✅ \n{santander_status}'        
        except Exception as e: return f'❌ Erro ao acessar banco santander: {e}'
    
    if command == 'bv': # executar roteiro do santander
        try:
                driver = await abrir_navegador(browser='chrome')
                print(f' ✅🌐  Webdriver acessado com sucesso   ✅ ')
                bv_status = await acessar_bv(driver, cliente)
                print(f' ✅🏦  Banco BV automatizado com sucesso   ✅ \n{bv_status}')
                return f' ✅🏦  Banco BV automatizado com sucesso   ✅ \n{bv_status}'        
        except Exception as e: return f'❌ Erro ao acessar Banco BV: {e}'
    
    
    
    else: # executar comando no terminal linux
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
