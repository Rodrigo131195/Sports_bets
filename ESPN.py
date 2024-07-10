from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# URL to scrape
url = 'https://www.espn.com/college-football/qbr'

# Set up Selenium WebDriver (headless mode)
options = Options()
options.headless = True
service = Service(executable_path='path/to/chromedriver')  # Adjust the path to your ChromeDriver
driver = webdriver.Chrome(service=service, options=options)

def scrape_data(driver):
    # Load the page
    driver.get(url)
    time.sleep(3)  # Allow some time for the page to load

    # Keep clicking "Show More" until it's no longer available
    while True:
        try:
            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@class="AnchorLink loadMore__link"]'))
            )
            show_more_button.click()
            time.sleep(2)  # Allow time for new data to load
        except Exception as e:
            print("No more 'Show More' button or error occurred:", e)
            break

    # Get the page source and parse it with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup

def parse_data(soup):
    # Extract data from the table
    table = soup.find('table')
    if table:
        # Extract header for RK and NAME
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
        # Create DataFrame
        df = pd.DataFrame(data, columns=headers + [f'VALUE_{i+1}' for i in range(9)])
        return df
    else:
        print(f"No table found in the URL: {url}")
        return None

# Scrape and parse data
soup = scrape_data(driver)
df = parse_data(soup)

# Save DataFrame to a CSV file without row indices
if df is not None:
    df.to_csv('output.csv', index=False)
    print("Data has been saved to 'output.csv'.")
else:
    print("No data scraped.")

# Close the driver
driver.quit()




















