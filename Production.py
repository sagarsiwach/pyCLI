import csv
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import httpx

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Read configuration from CSV
def read_config():
    with open('config.csv', mode='r') as file:
        reader = csv.DictReader(file)
        return next(reader)  # Assuming there's only one row of configuration

# Write updated configuration to CSV
def write_config(config):
    with open('config.csv', mode='w', newline='') as file:
        fieldnames = ['username', 'password', 'production_loops', 'storage_loops', 'headless',
                      'production_completed', 'storage_completed', 'executions_per_second', 'executions_per_minute',
                      'executions_per_hour', 'executions_last_hour', 'current_production', 'current_storage']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(config)

config = read_config()

# Setup Firefox options
options = Options()
options.headless = config['headless'].lower() == 'true'

# Function to initialize WebDriver
def initialize_driver():
    global driver
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    options.profile = firefox_profile
    driver = webdriver.Firefox(options=options)
    logging.info("WebDriver initialized")

# Function to accept cookies
def accept_cookies():
    try:
        WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.ID, "cookie__btn"))).click()
        logging.info("Cookies accepted")
    except Exception as e:
        logging.error(f"Error accepting cookies: {e}")

# Login function
def login():
    while True:
        try:
            driver.get("https://www.gotravspeed.com")
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "name"))).send_keys(config['username'])
            driver.find_element(By.ID, "password").send_keys(config['password'])
            driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//h2/font[contains(text(),'Fun')]/ancestor::div[1]"))).click()
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'default__button-o-login')]"))).click()
            return
        except Exception as e:
            print("Error during login:", e)
            
# Function to handle errors during execution
def handle_error():
    try:
        continue_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Continue')]")))
        continue_button.click()
    except Exception as e:
        logging.error("Error handling failed, trying to re-login:", e)
        login()

# Asynchronous function to increase production
async def increase_production_async(loop_count):
    async with httpx.AsyncClient() as client:
        start_time = time.time()
        for _ in range(loop_count):
            try:
                # Extract cookies from Selenium and set them in the HTTPX client
                cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
                client.cookies = httpx.Cookies(cookies)

                # Send a GET request to retrieve the key for increasing production
                get_response = await client.get("https://fun.gotravspeed.com/buy2.php?t=0")
                soup = BeautifulSoup(get_response.text, 'html.parser')
                key = soup.find('input', {'name': 'key'})['value']

                # Send a POST request to increase production
                data = {'selected_res': 4, 'xor': 100, 'key': key}
                post_response = await client.post("https://fun.gotravspeed.com/buy2.php?t=0&Shop=done", data=data)
                logging.info(f"Resource Increased")

                # Update the CSV with loop progress and speed
                config['production_completed'] = str(int(config['production_completed']) + 1)
                elapsed_time = time.time() - start_time
                config['executions_per_second'] = str(1 / elapsed_time)
                config['executions_per_minute'] = str(60 / elapsed_time)
                config['executions_per_hour'] = str(3600 / elapsed_time)
                write_config(config)
            except Exception as e:
                logging.error(f"Error during production increase: {e}")

# Asynchronous function to increase storage
async def increase_storage_async(loop_count):
    async with httpx.AsyncClient() as client:
        start_time = time.time()
        for _ in range(loop_count):
            try:
                # Extract cookies from Selenium and set them in the HTTPX client
                cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
                client.cookies = httpx.Cookies(cookies)

                # Send a GET request to retrieve the key for increasing storage
                get_response = await client.get("https://fun.gotravspeed.com/buy2.php?t=2")
                soup = BeautifulSoup(get_response.text, 'html.parser')
                key = soup.find('input', {'name': 'key'})['value']

                # Send a POST request to increase storage
                data = {'selected_res': 4, 'xor': 100, 'key': key}
                post_response = await client.post("https://fun.gotravspeed.com/buy2.php?t=2&Shop=done", data=data)
                logging.info(f"Storage Increased")

                # Update the CSV with loop progress and speed
                config['storage_completed'] = str(int(config['storage_completed']) + 1)
                elapsed_time = time.time() - start_time
                config['executions_per_second'] = str(1 / elapsed_time)
                config['executions_per_minute'] = str(60 / elapsed_time)
                config['executions_per_hour'] = str(3600 / elapsed_time)
                write_config(config)
            except Exception as e:
                logging.error(f"Error during storage increase: {e}")

# Main flow
initialize_driver()
accept_cookies()
login()

while True:
    try:
        # Call asynchronous functions
        increase_production_async(int(config['production_loops']))
        increase_storage_async(int(config['storage_loops']))
    except Exception as e:
        logging.error(f"Error encountered: {e}. Reinitializing driver and checking connections before retrying.")
        driver.quit()
        initialize_driver()
        login()
