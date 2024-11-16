from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

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

# Close the WebDriver
driver.quit()

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

# Display the DataFrame
print(df)
