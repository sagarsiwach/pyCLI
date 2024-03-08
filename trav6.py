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
server_user = "ANDANA"  # or "M16"
global_village_number = 1  # Used for renaming the secondary villages

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
        WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "cookie__btn"))).click()
        logging.info("Cookies accepted")
    except Exception as e:
        logging.error(f"Error accepting cookies: {e}")

# Function to log in
# Function to log in
# def login():
#     try:
#         driver.get("https://www.gotravspeed.com")
#         WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "name"))).send_keys(username)
#         driver.find_element(By.ID, "password").send_keys(password)
#         driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
#         WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//h2/font[contains(text(),'Fun')]/ancestor::div[1]"))).click()
        
#         # Select the server user
#         if server_user == "DRAVAZ":
#             WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Login as DRAVAZ')]"))).click()
#         elif server_user == "M16":
#             WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Login as M16')]"))).click()
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
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "name"))).send_keys(username)
            driver.find_element(By.ID, "password").send_keys(password)
            driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//h2/font[contains(text(),'Fun')]/ancestor::div[1]"))).click()
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'default__button-o-login')]"))).click()
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
        construct_link = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, f"//a[contains(@href, 'id={position_id}&b={building_id}')]"))
        )
        construct_link.click()
        logging.info(f"Clicked on 'Construct buildings' for building {building_id} at position {position_id}")
    except Exception as e:
        logging.error(f"Error building {building_id} at position {position_id}: {e}")




def build_and_upgrade(position_id, building_id, loop):
    try:
        # Build the building if it doesn't exist
        build_building(position_id, building_id)

        # Upgrade the building to the target level
        for _ in range(loop):
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
            upgrade_link = WebDriverWait(driver, 3).until(
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
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='buildDuration']"))
            )
            time.sleep(0.5)  # Add a short delay to ensure the upgrade is processed

    except Exception as e:
        logging.error(f"Error upgrading building at position {position_id}: {e}")


def upgrade_resource(position_id):
    try:
        # Navigate to the specific building page
        driver.get(f"https://fun.gotravspeed.com/village1.php")
        time.sleep(0.5)  # Add a short delay to ensure the page is loaded
        driver.get(f"https://fun.gotravspeed.com/build.php?id={position_id}")
        logging.info(f"Navigated to building page for position {position_id}")

        for _ in range(20):
            time.sleep(0.5)  # Add a short delay to ensure the page is loaded
            # Find the "upgrade to level" link and click it
            upgrade_link = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//p[@id='contract']/a[contains(@class, 'build')]"))
            )
            upgrade_link.click()
            logging.info(f"Clicked on upgrade link for position {position_id}")

            # Check if the building is fully upgraded
            build_div = driver.find_element(By.ID, "build")
            if "Updated" in build_div.text:
                logging.info("Building is fully upgraded.")
                break  # Break out of the loop if the building is fully upgraded

            # Wait for the upgrade to complete before proceeding to the next level
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='buildDuration']"))
            )
            time.sleep(0.5)  # Add a short delay to ensure the upgrade is processed

    except Exception as e:
        logging.error(f"Error upgrading building at position {position_id}: {e}")

        
        
def build_and_upgrade_resource(position_id):
    try:
        for _ in range(10):
            try:
                upgrade_resource(position_id)
            except Exception as e:
                logging.error(f"Error during upgrade: {e}. Continuing to next level.")
                continue

    except Exception as e:
        logging.error(f"Error encountered during build and upgrade: {e}")


def start_celebration(times=10000):
    town_hall_id = 35  # Adjust this to the correct ID for your Town Hall
    for _ in range(times):
        try:
            # Navigate to the Town Hall
            driver.get(f"https://fun.gotravspeed.com/build.php?id={town_hall_id}")
            logging.info("Navigated to Town Hall")

            # Start the Large Celebration
            large_celebration_link = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'a=2')]"))
            )
            large_celebration_link.click()
            logging.info("Started Large Celebration")

            # Wait for the celebration to be acknowledged before starting the next one
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Updated Town Hall Fully')]"))
            )

        except Exception as e:
            logging.error(f"Error during celebration: {e}")
            # Handle the error appropriately (e.g., re-login, retry, etc.)


    
    
def build_capital_village():
    build_and_upgrade(position_id=26, building_id=15, loop=20)
    build_and_upgrade_resource(position_id=1)
    build_and_upgrade_resource(position_id=2)
    build_and_upgrade_resource(position_id=3)
    build_and_upgrade_resource(position_id=4)
    build_and_upgrade_resource(position_id=5)
    build_and_upgrade_resource(position_id=6)
    build_and_upgrade_resource(position_id=7)
    build_and_upgrade_resource(position_id=8)
    build_and_upgrade_resource(position_id=9)
    build_and_upgrade_resource(position_id=10)
    build_and_upgrade_resource(position_id=11)
    build_and_upgrade_resource(position_id=12)
    build_and_upgrade_resource(position_id=13)
    build_and_upgrade_resource(position_id=14)
    build_and_upgrade_resource(position_id=15)
    build_and_upgrade_resource(position_id=16)
    build_and_upgrade_resource(position_id=17)
    build_and_upgrade_resource(position_id=18)
    build_and_upgrade(position_id=39, building_id=16, loop=20)
    build_and_upgrade(position_id=40, building_id=33, loop=20)
    build_and_upgrade(position_id=25, building_id=19, loop=20)
    build_and_upgrade(position_id=33, building_id=22, loop=20)
    build_and_upgrade(position_id=30, building_id=25, loop=20)
    build_and_upgrade(position_id=29, building_id=13, loop=20)
    build_and_upgrade(position_id=21, building_id=12, loop=20)
    build_and_upgrade(position_id=34, building_id=7, loop=10)
    build_and_upgrade(position_id=31, building_id=5, loop=10)
    build_and_upgrade(position_id=27, building_id=6, loop=10)
    build_and_upgrade(position_id=24, building_id=37, loop=20)
    build_and_upgrade(position_id=23, building_id=44, loop=1)
    build_and_upgrade(position_id=22, building_id=11, loop=20)
    build_and_upgrade(position_id=20, building_id=17, loop=20)
    build_and_upgrade(position_id=19, building_id=20, loop=20)
    build_and_upgrade(position_id=28, building_id=21, loop=20)
    build_and_upgrade(position_id=32, building_id=14, loop=20)
    build_and_upgrade(position_id=35, building_id=24, loop=20)
    build_and_upgrade(position_id=38, building_id=18, loop=20)
    build_and_upgrade(position_id=37, building_id=27, loop=20)
    





# Function to handle errors during execution
def handle_error():
    try:
        continue_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Continue')]")))
        continue_button.click()
    except Exception as e:
        logging.error("Error handling failed, trying to re-login:", e)
        login()

def train_settlers_concurrently():
    def send_train_request():
        response = requests.post(url, headers=headers, data=settlers_data, cookies=cookies)
        if response.status_code == 200:
            logging.info("Training Settlers in the current village")
        else:
            logging.error(f"Error during Settlers training: {response.status_code}")

    try:
        url = "https://fun.gotravspeed.com/build.php?id=30"
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        }
        settlers_data = "tf%5B20%5D=3&s1.x=50&s1.y=8"  # Set the quantity of settlers to train
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}

        with ThreadPoolExecutor(max_workers=1) as executor:
            futures = [executor.submit(send_train_request) for _ in range(1)]
            for future in concurrent.futures.as_completed(futures):
                pass  # You can handle each future's result or exception here if needed

    except Exception as e:
        logging.error(f"Error during Settlers training in the current village: {e}")



def train_settlers_and_find_new_village():
    residence_id = 30  # Adjust this to the correct ID for your Residence

    time.sleep(0.5)  # Add a short delay to ensure the page is loaded
    # Navigate to the Residence
    driver.get(f"https://fun.gotravspeed.com/build.php?id=30")
    logging.info("Navigated to Residence")
    time.sleep(0.5)

    # # Train 3 Settlers
    # max_settlers_link = WebDriverWait(driver, 3).until(
    #     EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick, '_tf30')]"))
    # )
    # max_settlers_link.click()
    # logging.info("Settlers quantity set to maximum")
    # time.sleep(0.5)

    # train_button = driver.find_element(By.ID, "btn_train")
    # train_button.click()
    train_settlers_concurrently()
    logging.info("Training 3 Settlers")
    time.sleep(0.5)

    # Wait for the settlers to be trained before proceeding
    # Add any necessary waiting logic here

    # Navigate to the Map
    driver.get("https://fun.gotravspeed.com/map.php")
    logging.info("Navigated to Map")
    time.sleep(0.5)

    # Find a suitable spot for the new village
    for village_id in range(70000, 80001):
        driver.get(f"https://fun.gotravspeed.com/village3.php?id={village_id}")
        village_options = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "options"))
        )
        if "building a new village" in village_options.text:
            # Found a suitable spot, proceed with next steps
            break

    time.sleep(0.5)

    # Click on "building a new village"
    build_new_village_link = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'building a new village')]"))
    )
    build_new_village_link.click()
    logging.info("Clicked on 'building a new village'")
    time.sleep(0.5)

    # Click on the OK button to confirm
    ok_button = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.ID, "btn_ok"))
    )
    ok_button.click()
    logging.info("Clicked on OK button to confirm new village")
    time.sleep(0.5)

    # Handle the new village popup
    continue_link = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '» continue')]"))
    )
    continue_link.click()
    logging.info("Clicked on Continue in the new village popup")
    time.sleep(0.5)



# Function to switch to the 0000 village
def switch_to_0000_village():
    try:
        driver.get("https://fun.gotravspeed.com/village1.php?vid=5231")
        logging.info("Switched to the 0000 village")
    except Exception as e:
        logging.error(f"Error switching to the 0000 village: {e}")
        
        
def rename_village(village_id, village_name):
    # Navigate to the profile page
    driver.get(f"https://fun.gotravspeed.com/dorf2.php?vid={village_id}")

    # Click on the "Change village name" link
    change_name_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Change village name')]"))
    )
    change_name_link.click()

    # Wait for the village name input to be clickable
    village_name_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "dname"))
    )

    # Clear the input and type the new village name
    village_name_input.clear()
    village_name_input.send_keys(village_name)

    # Click the "ok" button to save the changes
    ok_button = driver.find_element_by_id("btn_ok")
    ok_button.click()
    
def get_village_ids(excluded_ids):
    driver.get("https://fun.gotravspeed.com/dorf1.php")
    village_links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@id='vlist']//a[contains(@href, 'newdid=')]"))
    )
    village_ids = [link.get_attribute("href").split('=')[-1] for link in village_links]
    return [vid for vid in village_ids if vid not in excluded_ids]


def switch_to_village(village_id):
    try:
        driver.get(f"https://fun.gotravspeed.com/dorf1.php?newdid={village_id}")
        logging.info(f"Switched to the village with ID {village_id}")
    except Exception as e:
        logging.error(f"Error switching to the village with ID {village_id}: {e}")


def master_function():
    global global_village_number
    max_villages = 10  # Set the maximum number of villages you want

    # Navigate to the capital village and start celebrations
    switch_to_village(capital_village_id)  # Replace capital_village_id with the actual ID
    for _ in range(10000):
        start_celebration()

    while True:
        # Find and settle a new village
        train_settlers_and_find_new_village()

        # Get the list of current village IDs
        current_village_ids = get_village_ids(excluded_village_ids)

        # If the number of villages reaches the limit, break the loop
        if len(current_village_ids) >= max_villages:
            break

        # Switch to the newest village and rename it
        newest_village_id = current_village_ids[-1]
        switch_to_village(newest_village_id)
        rename_village(newest_village_id, f"{global_village_number:04}")
        global_village_number += 1

        # Build the secondary village
        build_secondary_village()



        
def build_secondary_village():

    # rename_village()    
    build_and_upgrade(position_id=26, building_id=15, loop=20)
    build_and_upgrade(position_id=39, building_id=16, loop=20)
    build_and_upgrade(position_id=40, building_id=33, loop=20)
    build_and_upgrade(position_id=25, building_id=19, loop=20)
    build_and_upgrade(position_id=33, building_id=22, loop=20)
    build_and_upgrade(position_id=30, building_id=25, loop=20)
    build_and_upgrade(position_id=34, building_id=7, loop=10)
    build_and_upgrade(position_id=31, building_id=5, loop=10)
    build_and_upgrade(position_id=27, building_id=6, loop=10)
    build_and_upgrade(position_id=24, building_id=37, loop=20)
    build_and_upgrade(position_id=24, building_id=44, loop=1)
    build_and_upgrade(position_id=37, building_id=27, loop=20)

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
        build_secondary_village()
        start_celebration(500)
        train_settlers_and_find_new_village()
    except Exception as e:
        logging.error(f"Error encountered: {e}. Reinitializing driver and checking connections before retrying.")
        driver.quit()
        initialize_driver()
        check_internet_connection()
        check_host()
        login()
