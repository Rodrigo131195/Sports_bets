from bs4 import BeautifulSoup
import requests
import pandas as pd

# URLs to scrape
urls = [
    'https://www.ncaa.com/stats/football/fbs/current/team/28',
    'https://www.ncaa.com/stats/football/fbs/current/team/28/p2',
    'https://www.ncaa.com/stats/football/fbs/current/team/28/p3'
]

# Set a custom User-Agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Function to scrape data from a given URL
def scrape_data(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find the table with the specified class name
        table = soup.find('table', class_='block-stats__stats-table')
        # Extract data from the table
        if table:
            # Extract table headers
            headers = [header.text.strip() for header in table.find_all('th')]
            # Extract table rows
            data = []
            rows = table.find_all('tr')
            for row in rows[1:]:  # Exclude header row
                values = [value.text.strip() for value in row.find_all('td')]
                data.append(values)
            # Create DataFrame
            df = pd.DataFrame(data, columns=headers)
            return df
        else:
            print(f"No table found in the URL: {url}")
            return None
    else:
        print(f"Failed to fetch the URL: {url}. Status code: {response.status_code}")
        return None

# Scrape data from each URL and concatenate the results
dfs = []
for url in urls:
    df = scrape_data(url, headers)
    if df is not None:
        dfs.append(df)

# Concatenate DataFrames
if dfs:
    final_df = pd.concat(dfs, ignore_index=True)
    # Save DataFrame to a CSV file without row indices
    final_df.to_csv('output.csv', index=False)
    print("Data has been saved to 'output.csv'.")
else:
    print("No data scraped.")
