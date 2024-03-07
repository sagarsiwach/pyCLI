from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import logging
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import random

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
username = "givova"
password = "1977"
uid = 13  # User ID for attacking and training troops
excluded_village_ids = ['4382']
# excluded_village_ids = ['155966', '155967','155964', '156367','155968','155164','155768','4382']
production_loops = 1100000
storage_loops = 100000
total_production_done = 0
total_storage_done = 0
server_user = "ANDANA"  # or "M16"


# Setup Firefox options
options = Options()
options.headless = True

# Function to initialize WebDriver
def initialize_driver():
    global driver
    driver = webdriver.Firefox(options=options)
    logging.info("WebDriver initialized")

# Function to check internet connection
def check_internet_connection():
    while True:
        try:
            requests.get("https://www.google.com", timeout=5)
            logging.info("Internet connection is available")
            return True
        except requests.ConnectionError:
            logging.warning("No internet connection. Retrying...")
            time.sleep(1)

# Function to check host availability
def check_host():
    while True:
        try:
            response = requests.get("https://www.gotravspeed.com", timeout=5)
            if response.status_code == 200:
                logging.info("Host is available")
                return True
        except requests.RequestException:
            logging.warning("Host error. Retrying...")
            time.sleep(1)

# Function to accept cookies
def accept_cookies():
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "cookie__btn"))).click()
        logging.info("Cookies accepted")
    except Exception as e:
        logging.error(f"Error accepting cookies: {e}")


def login():
    while True:
        try:
            driver.get("https://www.gotravspeed.com")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name"))).send_keys(username)
            driver.find_element(By.ID, "password").send_keys(password)
            driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//h2/font[contains(text(),'Fun')]/ancestor::div[1]"))).click()
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'default__button-o-login')]"))).click()
            return
        except Exception as e:
            print("Error during login:", e)
            check_internet_connection()
            check_host()


# Function to increase production
def increase_production():
    global total_production_done
    start_time = time.time()
    try:
        driver.get("https://fun.gotravspeed.com/buy2.php?t=0")
        for i in range(production_loops):
            WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.NAME, "selected_res")))[3].click()
            driver.find_element(By.NAME, "xor").send_keys("100x")
            driver.find_element(By.ID, "sendbutton").click()
            total_production_done += 1
            elapsed_time = time.time() - start_time
            speed = total_production_done / (elapsed_time / 60)
            logging.info(f"Resource production increased: {total_production_done} done, {production_loops-i-1} remaining in this loop, {production_loops-total_production_done} total remaining. Speed: {speed:.2f} executions/minute")
            

    except Exception as e:
        logging.error("Error during production increase:", e)
        handle_error()




# Function to handle errors during execution
def handle_error():
    try:
        continue_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Continue')]")))
        continue_button.click()
    except Exception as e:
        logging.error("Error handling failed, trying to re-login:", e)
        login()


# Main flow
initialize_driver()
check_internet_connection()
check_host()
accept_cookies()
login()


while True:
    try:

        increase_production()
    except Exception as e:
        logging.error(f"Error encountered: {e}. Reinitializing driver and checking connections before retrying.")
        driver.quit()
        initialize_driver()
        check_internet_connection()
        check_host()
        login()
