from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
username = "scar"
password = "fiverr"
production_loops = 5
storage_loops = 5

# Firefox Options
options = Options()
options.headless = True

# Sessions
session = requests.Session()

# Internet Connection
def check_internet_connection():
    try:
        requests.get("https://www.google.com", timeout=5)
        logging.info("Internet connection is available")
        return True
    except requests.ConnectionError:
        logging.warning("No internet connection. Retrying...")
        time.sleep(1)
        return False

# Host
def check_host():
    try:
        response = requests.get("https://www.gotravspeed.com", timeout=5)
        if response.status_code == 200:
            logging.info("Host is available")
            return True
    except requests.RequestException:
        logging.warning("Host error. Retrying...")
        time.sleep(1)
        return False

# Accept Cookies
def accept_cookies(driver):
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "cookie__btn"))).click()
        logging.info("Cookies accepted")
    except Exception as e:
        logging.error(f"Error accepting cookies: {e}")

# Login
def login():
    driver = webdriver.Firefox(options=options)
    driver.get("https://www.gotravspeed.com")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name"))).send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//h2/font[contains(text(),'Fun')]/ancestor::div[1]"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'default__button-o-login')]"))).click()
    accept_cookies(driver)
    cookies = driver.get_cookies()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    driver.quit()

# Increase Production
def increase_production(loop_count):
    for _ in range(loop_count):
        try:
            response = session.get("https://fun.gotravspeed.com/buy2.php?t=0")
            logging.info(f"GET Request to increase production: {response.url}")
            soup = BeautifulSoup(response.text, 'html.parser')
            key = soup.find('input', {'name': 'k'})['value']
            data = {'k': key}
            post_response = session.post("https://fun.gotravspeed.com/buy2.php?t=0&Shop=done", data=data)
            logging.info(f"POST Request to increase production: {post_response.url} with data {data}")
            if post_response.status_code == 302:
                logging.info("Production increased successfully")
            else:
                logging.error(f"Failed to increase production. Status code: {post_response.status_code}")
        except Exception as e:
            logging.error(f"Error during production increase: {e}")
            handle_error()

# Increase Storage
def increase_storage(loop_count):
    for _ in range(loop_count):
        try:
            response = session.get("https://fun.gotravspeed.com/buy2.php?t=2")
            logging.info(f"GET Request to increase storage: {response.url}")
            soup = BeautifulSoup(response.text, 'html.parser')
            key = soup.find('input', {'name': 'k'})['value']
            data = {'k': key}
            post_response = session.post("https://fun.gotravspeed.com/buy2.php?t=2&Shop=done", data=data)
            logging.info(f"POST Request to increase storage: {post_response.url} with data {data}")
            if post_response.status_code == 302:
                logging.info("Storage increased successfully")
            else:
                logging.error(f"Failed to increase storage. Status code: {post_response.status_code}")
        except Exception as e:
            logging.error(f"Error during storage increase: {e}")
            handle_error()

# Handle Error
def handle_error():
    logging.error("An error occurred, trying to re-login.")
    login()

# Main Flow
def main():
    check_internet_connection()
    check_host()
    login()
    increase_production(production_loops)
    increase_storage(storage_loops)

if __name__ == "__main__":
    main()
