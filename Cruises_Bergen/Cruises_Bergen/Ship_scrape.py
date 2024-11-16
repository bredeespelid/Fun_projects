from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# Set up Chrome options for headless mode
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920x1080")
options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)

# Initialize the WebDriver with options
driver = webdriver.Chrome(options=options)

# DataFrame with ship details
ships_data = {
    'ANKOMST': ['2024-08-25'],
    'SKIP': ['Carnival Horizon'],
    'SKIPSTYPE': ['Cruiseskip'],
    'FORTØYNING': ['Mooring 1'],
    'AVGANGSDATO': ['2024-08-31'],
    'STATUS': ['Scheduled']
}

df = pd.DataFrame(ships_data)

# Function to extract Passengers
def get_ship_details(ship_name):
    driver.get('https://www.cruisemapper.com/ships')

    # Find the search box and enter the ship name
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'typeahead'))
    )
    search_box.clear()
    search_box.send_keys(ship_name)

    # Wait for suggestions and click the first one
    time.sleep(2)  # Wait for suggestions to appear
    suggestion = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.tt-suggestion'))
    )
    suggestion.click()

    # Wait for the ship specs to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'specificationTable'))
    )

    # Parse the page
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Find the right table with passengers
    tables = soup.find_all('table', class_='table-striped')

    # Extract Passengers from the second table (pull-right)
    if len(tables) > 1:
        right_table = tables[1]  # The second table on the right
        passengers_row = right_table.find('td', string='Passengers')
        if passengers_row:
            passengers_text = passengers_row.find_next_sibling('td').text.strip()
            
            # Extract the upper limit of passengers
            if '-' in passengers_text:
                passengers = passengers_text.split('-')[1].strip()
            else:
                passengers = passengers_text
        else:
            passengers = 'N/A'
    else:
        passengers = 'N/A'

    return passengers

# Iterate over each ship and update the DataFrame
for index, row in df.iterrows():
    passengers = get_ship_details(row['SKIP'])
    df.at[index, 'PASSENGERS'] = passengers

# Close the WebDriver
driver.quit()

# Display the updated DataFrame
print(df)
