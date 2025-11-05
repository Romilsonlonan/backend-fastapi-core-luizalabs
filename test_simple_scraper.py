#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

# Teste simples do scraper
url = "https://www.espn.com.br/futebol/time/elenco/_/id/3454/ordenar/position/dir/desce/bra.cr_vasco_da_gama"

print("Testando scraper ESPN...")
print(f"URL: {url}")

try:
    # Faz requisição com headers de navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procura a tabela específica - agora usa a classe Table simples
        table = soup.find('table', class_='Table')
        
        if table:
            print("✅ Tabela encontrada!")
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                print(f"Linhas: {len(rows)}")
                
                # Mostra primeiros 3 jogadores
                for i, row in enumerate(rows[:3]):
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        name = cols[1].text.strip()[:30]
                        position = cols[2].text.strip()[:20]
                        print(f"  {i+1}. {name} - {position}")
            else:
                print("❌ Tbody não encontrado")
        else:
            print("❌ Tabela não encontrada")
            # Mostra todas as tabelas
            tables = soup.find_all('table')
            print(f"Tabelas encontradas: {len(tables)}")
            for i, t in enumerate(tables[:3]):
                print(f"  Tabela {i+1}: {t.get('class', 'sem classe')}")
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
