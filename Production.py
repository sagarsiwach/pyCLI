from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
import os
import time
import requests
import re
import logging
import concurrent.futures
from selenium.common.exceptions import TimeoutException
from concurrent.futures import ThreadPoolExecutor
import random
import json


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

session = requests.Session()


# Configuration
username = "scar"
password = "fiverr"
production_loops = 10000
storage_loops = 10000

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






# Increase Production
def increase_production(loop_count):
    for _ in range(loop_count):
        try:
            # Extract cookies from Selenium and set them in the requests session
            selenium_cookies = driver.get_cookies()
            for cookie in selenium_cookies:
                session.cookies.set(cookie['name'], cookie['value'])

            # Send a GET request to retrieve the key for increasing production
            get_response = session.get("https://fun.gotravspeed.com/buy2.php?t=0")
            # logging.info(f"GET Request to increase production: {get_response.url}")
            soup = BeautifulSoup(get_response.text, 'html.parser')
            key = soup.find('input', {'name': 'key'})['value']

            # Send a POST request to increase production
            data = {'selected_res': 4, 'xor': 100, 'key': key}
            post_response = session.post("https://fun.gotravspeed.com/buy2.php?t=0&Shop=done", data=data)
            logging.info(f"Resource Incrased")

            # if post_response.status_code == 302:
            #     logging.info("Production increased successfully")
            # # else:
            #     logging.error(f"Failed to increase production. Status code: {post_response.status_code}")
        except Exception as e:
            logging.error(f"Error during production increase: {e}")

# Increase Storage
def increase_storage(loop_count):
    for _ in range(loop_count):
        try:
            # Extract cookies from Selenium and set them in the requests session
            selenium_cookies = driver.get_cookies()
            for cookie in selenium_cookies:
                session.cookies.set(cookie['name'], cookie['value'])

            # Send a GET request to retrieve the key for increasing storage
            get_response = session.get("https://fun.gotravspeed.com/buy2.php?t=2")
            # logging.info(f"GET Request to increase storage: {get_response.url}")
            soup = BeautifulSoup(get_response.text, 'html.parser')
            key = soup.find('input', {'name': 'k'})['value']

            # Send a POST request to increase storage
            data = {'k': key}
            post_response = session.post("https://fun.gotravspeed.com/buy2.php?t=2&Shop=done", data=data)
            logging.info(f"Storage Increased")

            # if post_response.status_code == 302:
            #     logging.info("Storage increased successfully")
            # else:
            #     logging.error(f"Failed to increase storage. Status code: {post_response.status_code}")
        except Exception as e:
            logging.error(f"Error during storage increase: {e}")






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
# check_internet_connection()
check_host()
accept_cookies()
login()

while True:
    try:
        
        increase_production(production_loops)
        increase_storage(storage_loops)
        # rename_all_villages()
        # master_function()
        # rename_village(10829, "0000")
        # get_village_ids(excluded_village_ids)
        # build_and_upgrade(position_id=39, building_id=16)
        # build_capital_village()
        # build_secondary_village()
        # start_celebration(10000)
        # train_settlers_and_find_new_village()
    except Exception as e:
        logging.error(f"Error encountered: {e}. Reinitializing driver and checking connections before retrying.")
        driver.quit()
        initialize_driver()
        check_internet_connection()
        check_host()
        login()

