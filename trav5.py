from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import requests
import logging
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import random
import json


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
username = "scar"
password = "fiverr"
uid = 13  # User ID for attacking and training troops
excluded_village_ids = ['4382']
production_loops = 1
storage_loops = 1
total_production_done = 0
total_storage_done = 0
server_user = "ZXZ"  # or "M16"

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
        WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.ID, "cookie__btn"))).click()
        logging.info("Cookies accepted")
    except Exception as e:
        logging.error(f"Error accepting cookies: {e}")

# Function to log in
# Function to log in
# def login():
#     try:
#         driver.get("https://www.gotravspeed.com")
#         WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "name"))).send_keys(username)
#         driver.find_element(By.ID, "password").send_keys(password)
#         driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
#         WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, "//h2/font[contains(text(),'Fun')]/ancestor::div[1]"))).click()
        
#         # Select the server user
#         if server_user == "DRAVAZ":
#             WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Login as DRAVAZ')]"))).click()
#         elif server_user == "M16":
#             WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Login as M16')]"))).click()
#         else:
#             raise ValueError(f"Invalid server user: {server_user}")
        
#         logging.info(f"Logged in successfully as {server_user}")
#     except Exception as e:
#         logging.error(f"Error during login: {e}")
#         check_internet_connection()
#         check_host()

def login():
    while True:
        try:
            driver.get("https://www.gotravspeed.com")
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "name"))).send_keys(username)
            driver.find_element(By.ID, "password").send_keys(password)
            driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
            WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, "//h2/font[contains(text(),'Fun')]/ancestor::div[1]"))).click()
            WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'default__button-o-login')]"))).click()
            return
        except Exception as e:
            print("Error during login:", e)
            check_internet_connection()
            check_host()


def navigate_to_construction_page():
    try:
        # Navigate to the construction page with the correct URL format
        driver.get(f"https://fun.gotravspeed.com/village2.php?=BuildMode=1")
        logging.info("Navigated to construction page and enabled build mode")
    except Exception as e:
        logging.error(f"Error navigating to construction page: {e}")
        
        
        
        

def build_building(position_id, building_id):
    try:
        # Navigate to the Village Center
        driver.get(f"https://fun.gotravspeed.com/village2.php")
        logging.info("Navigated to Village Center")

        # Click on the empty position
        driver.get(f"https://fun.gotravspeed.com/build.php?id={position_id}")
        logging.info(f"Clicked on empty position {position_id}")
        
        time.sleep(1)  # Add a short delay to ensure the page is loaded

        # Find the "Construct buildings" link that matches the build and position ID
        construct_link = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, f"//a[contains(@href, 'id={position_id}&b={building_id}')]"))
        )
        construct_link.click()
        logging.info(f"Clicked on 'Construct buildings' for building {building_id} at position {position_id}")
    except Exception as e:
        logging.error(f"Error building {building_id} at position {position_id}: {e}")




def build_and_upgrade(position_id, building_id):
    try:
        # Build the building if it doesn't exist
        build_building(position_id, building_id)

        # Upgrade the building to the target level
        for _ in range(20):
            try:
                upgrade_building(position_id)
            except Exception as e:
                logging.error(f"Error during upgrade: {e}. Continuing to next level.")
                continue

    except Exception as e:
        logging.error(f"Error encountered during build and upgrade: {e}")
        
        

def upgrade_building(position_id):
    try:
        # Navigate to the specific building page
        driver.get(f"https://fun.gotravspeed.com/village2.php")
        time.sleep(0.5)  # Add a short delay to ensure the page is loaded
        driver.get(f"https://fun.gotravspeed.com/build.php?id={position_id}")
        logging.info(f"Navigated to building page for position {position_id}")

        for _ in range(20):
            # Find the "upgrade to level" link and click it
            upgrade_link = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[contains(@class, 'build') and contains(@href, 'village2.php?id={position_id}')]"))
            )
            upgrade_link.click()
            logging.info(f"Clicked on upgrade link for position {position_id}")

            # Check if the building is fully upgraded
            build_div = driver.find_element(By.ID, "build")
            if "Updated" in build_div.text:
                logging.info("Building is fully upgraded.")
                break  # Break out of the loop if the building is fully upgraded

            # Wait for the upgrade to complete before proceeding to the next level
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='buildDuration']"))
            )
            time.sleep(0.5)  # Add a short delay to ensure the upgrade is processed

    except Exception as e:
        logging.error(f"Error upgrading building at position {position_id}: {e}")


    
    
def build_capital_village():
    build_and_upgrade(position_id=26, building_id=15)
    build_and_upgrade(position_id=39, building_id=16)
    build_and_upgrade(position_id=40, building_id=33)
    build_and_upgrade(position_id=25, building_id=19)
    build_and_upgrade(position_id=33, building_id=22)
    build_and_upgrade(position_id=30, building_id=25)
    build_and_upgrade(position_id=29, building_id=13)
    build_and_upgrade(position_id=21, building_id=12)
    build_and_upgrade(position_id=34, building_id=7)
    build_and_upgrade(position_id=31, building_id=5)
    build_and_upgrade(position_id=27, building_id=6)
    build_and_upgrade(position_id=24, building_id=37)
    build_and_upgrade(position_id=23, building_id=44)
    build_and_upgrade(position_id=22, building_id=11)
    build_and_upgrade(position_id=20, building_id=17)
    build_and_upgrade(position_id=19, building_id=20)
    build_and_upgrade(position_id=28, building_id=21)
    build_and_upgrade(position_id=32, building_id=14)
    build_and_upgrade(position_id=35, building_id=24)
    build_and_upgrade(position_id=38, building_id=18)
    build_and_upgrade(position_id=37, building_id=27)
    





# Function to handle errors during execution
def handle_error():
    try:
        continue_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Continue')]")))
        continue_button.click()
    except Exception as e:
        logging.error("Error handling failed, trying to re-login:", e)
        login()



# Function to switch to the 0000 village
def switch_to_0000_village():
    try:
        driver.get("https://fun.gotravspeed.com/village1.php?vid=5231")
        logging.info("Switched to the 0000 village")
    except Exception as e:
        logging.error(f"Error switching to the 0000 village: {e}")

# Main flow
initialize_driver()
# check_internet_connection()
# check_host()
accept_cookies()
login()

while True:
    try:
        # build_and_upgrade(position_id=39, building_id=16)
        build_capital_village()
    except Exception as e:
        logging.error(f"Error encountered: {e}. Reinitializing driver and checking connections before retrying.")
        driver.quit()
        initialize_driver()
        check_internet_connection()
        check_host()
        login()
