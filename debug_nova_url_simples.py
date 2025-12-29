import re
import requests
from bs4 import BeautifulSoup

def debug_espn_url(url: str):
    """
    Fetches the ESPN URL and prints relevant HTML sections to debug scraping issues.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    print(f"🌐 Attempting to fetch URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for HTTP errors

        print(f"✅ Successfully fetched URL. Status Code: {response.status_code}")
        soup = BeautifulSoup(response.text, 'html.parser')

        print("\n--- HTML HEAD ---")
        print(soup.head)

        print("\n--- HTML BODY (first 500 chars) ---")
        print(str(soup.body)[:500])

        # Try to find the main div containing the squad tables
        squad_div = soup.find('div', id=re.compile(r'tbl-aug-\d+'))
        if squad_div:
            print(f"\n--- Found squad div with ID: {squad_div.get('id')} ---")
            print(str(squad_div)[:1000]) # Print first 1000 chars of the div
            
            tables = squad_div.find_all('table', class_='Table')
            if tables:
                print(f"\n--- Found {len(tables)} tables within the squad div ---")
                for i, table in enumerate(tables):
                    print(f"\n--- Table {i+1} Headers ---")
                    thead = table.find('thead')
                    if thead:
                        headers = [th.get_text(strip=True) for th in thead.find_all('th')]
                        print(headers)
                    else:
                        print("No thead found for this table.")
                    
                    print(f"--- Table {i+1} First 5 Rows ---")
                    tbody = table.find('tbody')
                    if tbody:
                        rows = tbody.find_all('tr')
                        for j, row in enumerate(rows[:5]):
                            cols = [td.get_text(strip=True) for td in row.find_all('td')]
                            print(f"Row {j+1}: {cols}")
                        if not rows:
                            print("No rows found in this table's tbody.")
                    else:
                        print("No tbody found for this table.")
            else:
                print("\n--- No tables with class 'Table' found within the squad div ---")
        else:
            print("\n--- No squad div (tbl-aug-XXXX) found. Searching for all tables directly. ---")
            tables = soup.find_all('table', class_='Table')
            if tables:
                print(f"\n--- Found {len(tables)} tables globally ---")
                for i, table in enumerate(tables):
                    print(f"\n--- Global Table {i+1} Headers ---")
                    thead = table.find('thead')
                    if thead:
                        headers = [th.get_text(strip=True) for th in thead.find_all('th')]
                        print(headers)
                    else:
                        print("No thead found for this global table.")
                    
                    print(f"--- Global Table {i+1} First 5 Rows ---")
                    tbody = table.find('tbody')
                    if tbody:
                        rows = tbody.find_all('tr')
                        for j, row in enumerate(rows[:5]):
                            cols = [td.get_text(strip=True) for td in row.find_all('td')]
                            print(f"Row {j+1}: {cols}")
                        if not rows:
                            print("No rows found in this global table's tbody.")
                    else:
                        print("No tbody found for this global table.")
            else:
                print("\n--- No tables with class 'Table' found anywhere on the page ---")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except Exception as e:
        print(f"❌ General Error: {e}")

if __name__ == "__main__":
    NEW_ESPN_URL = "https://www.espn.com.br/futebol/time/elenco/_/id/3454/liga/BRA.1/temporada/2025"
    debug_espn_url(NEW_ESPN_URL)
