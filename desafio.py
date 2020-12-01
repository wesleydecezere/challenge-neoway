# -*- encoding: utf-8 -*-

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import json

# Grab content from URL (Pegar conteúdo HTML a partir da URL)
url = "http://www.buscacep.correios.com.br/sistemas/buscacep/buscaFaixaCep.cfm"

print("Connecting...")

option = Options()
option.headless = True
driver = webdriver.Chrome(options=option)

driver.get(url)
driver.implicitly_wait(1)  # in seconds

print("\nThe URL \'%s\' was acessed with secess!" % url)

# Get all the UFs avaliable to search
uf_field = driver.find_element(By.NAME, "UF")
outer_text = uf_field.get_attribute('outerText')            

# Put it in a list and in a dict
uf_list = outer_text.split('\n')
uf = {x:[] for x in uf_list}

''' While there is any UF not searched '''
for uf_index in range(len(uf)):   

    # Select a UF from the uf_list to search
    field = Select(driver.find_element(By.NAME, "UF"))
    field.select_by_value(uf_list[uf_index])

    # Trigger the search
    driver.find_element(By.CLASS_NAME, "btn2.float-right").click()

    print("Getting data from the %s\'s UF..." % uf_list[uf_index])

    last_id = 1

    ''' While exist next page '''
    while True:         
        # Get the actual content
        element = driver.find_elements(By.CLASS_NAME, "tmptabela")
        html_content = element[len(element)-1].get_attribute('outerHTML')            

        # Parse HTML - BeaultifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find(name='table')

        # Data Structure Conversion - Pandas
        df_full = pd.read_html(str(table))[0]
        df = df_full[['Localidade', 'Faixa de CEP']]

        # Add an id for each record 
        df.insert(0,'Item',[i for i in range(last_id, last_id+len(df))])
        last_id = df['Item'][len(df)-1] + 1
        
        # Convert the data to a list of dicts and add it to a uf_dict
        uf[uf_list[uf_index]] += df.to_dict('records')

        try:
            # Go to the next page
            driver.find_element(By.LINK_TEXT, '[ Próxima ]').click()
        except NoSuchElementException:            
            # Go to new search
            driver.find_element(By.LINK_TEXT, '[ Nova Consulta ]').click()
            break

print("\nThe data from all the avaliable UFs was collected whit success!")
driver.quit()

# Dump and save the uf_dict to JSON file
with open('output.json', 'w', encoding='utf-8') as jp:
    js = json.dumps(uf, indent=2)
    jp.write(js)
    jp.close()

print("It was writed in JSON file named \'output.json\'.\n")
print("Press the enter key to finish the app...")
input()