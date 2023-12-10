# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 23:26:10 2023

@author: pedro
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_table_data(table):
    rows = table.find_all('tr')
    headers = [header.text.strip() for header in rows[0].find_all('td')]
    data = []
    for row in rows[1:]:  # Começa do segundo elemento para pular o cabeçalho
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append(cols)
    return headers, data

# Função para fazer o scraping de uma única data
def scrape_date(main_df, date):
    url = 'https://www2.bmf.com.br/pages/portal/bmfbovespa/boletim1/SistemaPregao1.asp'
    params = {
        'pagetype': 'pop',
        'caminho': 'Resumo Estatístico - Sistema Pregão',
        'Data': date.strftime('%d/%m/%Y'), 
        'Mercadoria': 'DI1'
    }

    # Constrói a URL com os parâmetros
    full_url = f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

    # Acessa a URL com Selenium
    driver.get(full_url)

    try: 
        # Espera pela presença de um elemento específico para garantir o carregamento
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//img[@alt='Ver Volume']")))
    
        # Clica no ícone para expandir a tabela
        expand_icon = driver.find_element(By.XPATH, "//img[@alt='Ver Volume']")
        expand_icon.click()
    
        # Aguarda novamente para garantir que a tabela foi expandida
        #time.sleep(5)  # Ajuste este tempo conforme necessário
    
        # Obtem o código-fonte da página
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
    
        # Encontra a primeira tabela pelo ID e extrai os dados
        tabela1 = soup.find('td', {'id': 'MercadoFut0'}).find('table')
        headers1, table_data1 = extract_table_data(tabela1)
        df1 = pd.DataFrame(table_data1, columns=headers1)
    
        # Encontra a segunda tabela pelo ID e extrai os dados
        tabela2 = soup.find('td', {'id': 'MercadoFut1'}).find('table')
        headers2, table_data2 = extract_table_data(tabela2)
        df2 = pd.DataFrame(table_data2, columns=headers2)
        
        # Encontra a segunda tabela pelo ID e extrai os dados
        tabela3 = soup.find('td', {'id': 'MercadoFut2'}).find('table')
        headers3, table_data3 = extract_table_data(tabela3)
        df3 = pd.DataFrame(table_data3, columns=headers3)
        
        # Concatena as tabelas horizontalmente
        combined_df = pd.concat([df1, df2, df3], axis=1)
    
        # Adiciona a coluna "Data" com a data correspondente
        combined_df['Data'] = date.strftime('%d/%m/%Y')
        
        # Concatena os dados deste dia ao DataFrame principal
        main_df = pd.concat([main_df, combined_df])
    
    except:
        
        print(f"Não foram encontrados dados para a data {date.strftime('%d/%m/%Y')}")
    
    return main_df

# Configuração do Selenium para abrir o Chrome
options = Options()
options.headless = True  # Roda em modo headless (sem abrir a janela do navegador)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Define o intervalo de datas
start_date = datetime.now() - timedelta(days=10*365)
end_date = datetime.now()
business_days = pd.bdate_range(start=start_date, end=end_date)
 
# DataFrame principal onde todos os dados serão acumulados
main_df = pd.DataFrame()

# Marca o tempo de início
start_time = time.time()

# Loop através de cada dia útil
for date in business_days:
    print (date)
    main_df = scrape_date(main_df, date)

# Marca o tempo de término
end_time = time.time()

# Calcula a duração
duration = end_time - start_time
print(f"Tempo de execução: {duration} segundos")

# Não esqueça de fechar o driver no final
driver.quit()
