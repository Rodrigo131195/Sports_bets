import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Base URL to scrape (initial page)
base_url = 'https://www.espn.com/college-football/qbr'
# URL for the AJAX request (actual URL for loading additional data)
ajax_url = 'https://site.web.api.espn.com/apis/fitt/v3/sports/football/college-football/qbr'

# Set up headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'  # Common header for AJAX requests
}

def get_page_content(url, params=None):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # Ensure the request was successful
    return response

def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Extract data from the table
    table = soup.find('table')
    if table:
        headers = ['RK', 'NAME']
        rows = table.find_all('tr')[1:]  # Skip the header row
        data = []
        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 2:
                rk = cells[0].text.strip()
                name = cells[1].text.strip()
                stats = [cell.text.strip() for cell in cells[2:]]
                data.append([rk, name] + stats)
        if data:
            df = pd.DataFrame(data, columns=headers + [f'VALUE_{i+1}' for i in range(len(data[0])-2)])
            return df
        else:
            print(f"No data found in the table on URL: {base_url}")
            return None
    else:
        print(f"No table found in the URL: {base_url}")
        return None

def parse_json(json_content):
    players = json_content.get('players', [])
    data = []
    for player in players:
        rk = player.get('rank')
        name = player.get('name')
        stats = [player.get(stat) for stat in ['value1', 'value2', 'value3']]  # Update these fields based on the JSON structure
        data.append([rk, name] + stats)
    if data:
        headers = ['RK', 'NAME'] + [f'VALUE_{i+1}' for i in range(len(data[0])-2)]
        df = pd.DataFrame(data, columns=headers)
        return df
    else:
        return None

# Get the initial page content (HTML)
try:
    page_content = get_page_content(base_url).text
    initial_data = parse_html(page_content)

    # List to store all the data
    all_data = []

    if initial_data is not None:
        all_data.append(initial_data)

    # Check for more data and iterate until no more data is available
    page_number = 2
    while True:
        params = {
            'region': 'us',
            'lang': 'en',
            'qbrType': 'seasons',
            'page': page_number,
            'sort': 'schedAdjQBR:desc'
        }
        try:
            print(f"Loading next page: {ajax_url} with params {params}")
            next_page_content = get_page_content(ajax_url, params=params).json()
            next_page_data = parse_json(next_page_content)
            if next_page_data is None or next_page_data.empty:
                print("No more data found on the next page.")
                break
            all_data.append(next_page_data)
            page_number += 1
            time.sleep(2)  # Allow time for new data to load
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            break

    # Combine all data into a single DataFrame
    if all_data:
        df = pd.concat(all_data, ignore_index=True)
        df.to_csv('output.csv', index=False)
        print("Data has been saved to 'output.csv'.")
    else:
        print("No data scraped.")

except requests.exceptions.RequestException as e:
    print(f"Error fetching or parsing data: {e}")

