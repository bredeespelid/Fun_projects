from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# Set up Chrome options for headless mode
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")  # Disable GPU acceleration
options.add_argument("--window-size=1920x1080")  # Set window size

# Initialize the WebDriver with options
driver = webdriver.Chrome(options=options)
driver.get('https://www.bergenhavn.no/anlopsliste')  # Replace with the actual URL

# Wait for the button to be present
button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Se full anløpsliste')]"))
)

# Click the button using JavaScript
driver.execute_script("arguments[0].click();", button)

# Wait for the list to load
WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, 'flex-row'))
)

# Get page source and parse with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Extract data
ships = []
for row in soup.find_all('div', class_='flex-row'):
    main_info = row.find('div', class_='flex w-full flex-col')
    if main_info:
        columns = main_info.find_all('span')
        if len(columns) >= 6:
            arrival = columns[0].text.strip()
            ship_name = columns[1].text.strip()
            ship_type = columns[2].text.strip()
            mooring = columns[3].text.strip()
            departure = columns[4].text.strip()
            status = columns[5].text.strip()

            # Filter to include only "Cruiseskip"
            if ship_type == "Cruiseskip":
                ships.append({
                    'ANKOMST': arrival,
                    'SKIP': ship_name,
                    'SKIPSTYPE': ship_type,
                    'FORTØYNING': mooring,
                    'AVGANGSDATO': departure,
                    'STATUS': status
                })

# Create a DataFrame
df = pd.DataFrame(ships)

# Dictionary to cache passenger information
passenger_cache = {}

# Function to extract Passengers from CruiseMapper
def get_ship_details(ship_name):
    # Check if ship is already in cache
    if ship_name in passenger_cache:
        return passenger_cache[ship_name]
    
    # Reinitialize WebDriver with options for headless browsing
    driver = webdriver.Chrome(options=options)
    
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

    # Store the result in the cache
    passenger_cache[ship_name] = passengers

    driver.quit()
    return passengers

# Iterate over each ship and update the DataFrame with Passengers
for index, row in df.iterrows():
    passengers = get_ship_details(row['SKIP'])
    df.at[index, 'PASSENGERS'] = passengers

# Display the updated DataFrame
print(df)
