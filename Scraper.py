from bs4 import BeautifulSoup
import requests
import pandas as pd

# URL of the page to scrape
base_url = 'https://247sports.com/season/2024-football/compositeteamrankings/'

# Set a custom User-Agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Function to scrape content from a given URL
def scrape_content(url, data):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract and append the desired data
        primary_elements = soup.find_all(class_='primary')
        team_elements = soup.find_all(class_='team')
        total_elements = soup.find_all(class_='total')
        star_comit_elements = soup.find_all(class_='star-commits-list')
        avg_elements = soup.find_all(class_='avg')
        points_elements = soup.find_all(class_='points')

        for primary, team, total, star_comit, avg, points in zip(primary_elements, team_elements, total_elements, star_comit_elements, avg_elements, points_elements):
            data.append({
                'Primary': primary.text.strip(),
                'Team': team.text.strip(),
                'Total': total.text.strip(),
                'Star Comit': star_comit.text.strip(),
                'Avg': avg.text.strip(),
                'Points': points.text.strip()
            })

        # Check if there's a "Load More" button
        load_more_button = soup.find('a', {'data-js': 'showmore'})
        if load_more_button:
            # Extract the URL from the button's href attribute
            load_more_url = load_more_button['href']
            # Recursively call scrape_content with the "Load More" URL
            scrape_content(load_more_url, data)

# Create an empty list to store the data
data = []

# Initial request to the base URL
scrape_content(base_url, data)

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(data)

# Save DataFrame to a CSV file without row indices
df.to_csv('output.csv', index=False)
