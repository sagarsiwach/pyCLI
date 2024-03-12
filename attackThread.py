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
from concurrent.futures import ThreadPoolExecutor
import random
import threading
import re
import requests
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
username = "SCAR"
password = "fiverr"
uid = 9  # User ID for attacking and training troops
excluded_village_ids = ['10829', '151986']
# excluded_village_ids = ['155966', '155967','155964', '156367','155968','155164','155768','4382']
production_loops = 1100000
storage_loops = 100000
total_production_done = 0
total_storage_done = 0
server_user = "ANDANA"  # or "M16"

# Set up ZAP as a proxy for requests
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080',
}
requests.proxies = proxies

# Setup Firefox options
options = Options()
options.headless = True

# Function to initialize WebDriver
def initialize_driver():
    global driver
    firefox_profile = webdriver.FirefoxProfile()
    # firefox_profile.set_preference('permissions.default.image', 2)
    options.profile = firefox_profile
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

# Function to log in
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

# Function to get village links and sort them in ascending order
def get_village_links():
    village_links = driver.find_elements(By.XPATH, "//table[@id='vlist']//a[contains(@href, '?vid=')]")
    villages = [(link.get_attribute("href"), link.text) for link in village_links]
    sorted_villages = sorted(villages, key=lambda x: x[1])
    return [village[0] for village in sorted_villages]

# Function to train Phalanxes in the first village concurrently
def train_phalanxes_concurrently():
    def send_train_request():
        response = requests.post(url, headers=headers, data=phalanxes_data, cookies=cookies)
        if response.status_code == 200:
            logging.info("Training Phalanxes in the current village")
        else:
            logging.error(f"Error during Phalanxes training: {response.status_code}")

    try:
        url = "https://fun.gotravspeed.com/build.php?id=19"
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
        phalanxes_data = "tf%5B21%5D=221117636153554570000&s1.x=50&s1.y=8"  # Change the troop ID and amount as needed
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(send_train_request) for _ in range(20)]
            for future in concurrent.futures.as_completed(futures):
                pass  # You can handle each future's result or exception here if needed

    except Exception as e:
        logging.error(f"Error during Phalanxes training in the current village: {e}")

# Function to train Phalanxes in other villages concurrently
def train_phalanxes_concurrently_in_other_villages():
    def send_train_request():
        response = requests.post(url, headers=headers, data=phalanxes_data, cookies=cookies)
        if response.status_code == 200:
            logging.info("Training Phalanxes in the current village")
        else:
            logging.error(f"Error during Phalanxes training: {response.status_code}")

    try:
        url = "https://fun.gotravspeed.com/build.php?id=19"
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
        phalanxes_data = "tf%5B26%5D=221117636153554570000&s1.x=50&s1.y=8"  # Adjust the amount as needed
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(send_train_request) for _ in range(4)]
            for future in concurrent.futures.as_completed(futures):
                pass  # You can handle each future's result or exception here if needed

    except Exception as e:
        logging.error(f"Error during Phalanxes training in other villages: {e}")

# Function to train troops in all villages concurrently
def train_troops_in_all_villages_concurrently():
    village_urls = get_village_links()

    for index, village_url in enumerate(village_urls):
        # Switch to the village
        driver.get(village_url)
        time.sleep(1)

        # Train Praetorians in the first village, tr2 in the others
        if index == 0:
            train_phalanxes_concurrently()
        else:
            train_phalanxes_concurrently_in_other_villages()

# Function to handle errors during execution
def handle_error():
    try:
        continue_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Continue')]")))
        continue_button.click()
    except Exception as e:
        logging.error("Error handling failed, trying to re-login:", e)
        login()

# Function to get the list of non-capital villages for a given player, excluding specified village IDs
def get_player_villages(uid, excluded_village_ids):
    try:
        driver.get(f"https://fun.gotravspeed.com/profile.php?uid={uid}")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "villages")))
        village_links = driver.find_elements(By.XPATH, "//table[@id='villages']//a[contains(@href, 'village3.php?id=')]")
        villages = []
        for link in village_links:
            village_id = link.get_attribute("href").split('=')[-1]
            if village_id not in excluded_village_ids:
                village_name = link.text
                village_url = f"https://fun.gotravspeed.com/v2v.php?id={village_id}"
                villages.append((village_name, village_url))
        sorted_villages = sorted(villages, key=lambda x: x[0])
        logging.info(f"Found {len(sorted_villages)} non-capital villages for player {uid} excluding village IDs {excluded_village_ids}")
        return sorted_villages
    except Exception as e:
        logging.error(f"Error getting non-capital villages for player {uid} excluding village IDs {excluded_village_ids}: {e}")
        
        
        
        
def attack_village(village_url):
    try:
        # Derive the village ID from the village URL
        village_id = village_url.split('=')[-1]

        # Define your headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.160 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://fun.gotravspeed.com",
            "Referer": village_url,
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }

        # Use cookies from Selenium session
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}

        # GET request to retrieve the key
        response = requests.get(village_url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(response.text, 'html.parser')
        key = soup.find('input', {'name': 'key'})['value']

        # Construct the data for the POST request
        data = {
            'id': village_id,
            'c': '4',  # Attack: raid
            't[21]': '5.0000000000000000000000e+18',  # Phalanx
            't[22]': '0',  # Swordsman
            't[23]': '0',  # Pathfinder
            't[24]': '0',  # Theutates Thunder
            't[25]': '0',  # Druidrider
            't[26]': '0',  # Haeduan
            't[27]': '0',  # Battering Ram
            't[28]': '0',  # Trebuchet
            't[29]': '0',  # Chief
            't[30]': '0',  # Settler
            'key': key
        }

        # Calculate content length
        content_length = sum(len(str(v)) for v in data.values()) + len('&'.join(data.keys()))

        # Update headers with content length
        headers['Content-Length'] = str(content_length)

        # POST request to send troops
        attack_response = requests.post("https://fun.gotravspeed.com/v2v.php", headers=headers, cookies=cookies, data=data)
        if attack_response.status_code == 200:
            print(f"Attacked village with ID {village_id}")
        else:
            print(f"Error attacking village with ID {village_id}: {attack_response.status_code}")

    except Exception as e:
        print(f"Error attacking village with ID {village_id}: {e}")

# Function to train troops without multithreading
def train_troops():
    try:
        url = "https://fun.gotravspeed.com/build.php?id=25"
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
        
        data = "tf%5B21%5D=521117636153554570000&s1.x=50&s1.y=8"
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}
        response = requests.post(url, headers=headers, data=data, cookies=cookies)
        if response.status_code == 200:
            logging.info("Training Praetorians in the current village")
        else:
            logging.error(f"Error during Praetorians training: {response.status_code}")
    except Exception as e:
        logging.error(f"Error during Praetorians training in the current village: {e}")

# Function to attack a village and then train troops
def attack_village_and_train_troops(village_url):
    switch_to_0000_village()
    train_troops()
    attack_village(village_url)
    # attack_village(village_url)

# Function to get the list of villages, attack 50 villages, do other jobs, then attack another 50 villages
# Function to get the list of villages, attack 50 villages, do other jobs, then attack another 50 villages
def get_villages_attack_and_train(uid, excluded_village_ids):
    non_capital_villages = get_player_villages(uid, excluded_village_ids)
    if non_capital_villages:
        random.shuffle(non_capital_villages)  # Shuffle the list of villages
        village_chunks = [non_capital_villages[i:i + 100] for i in range(0, len(non_capital_villages), 300)]
        for chunk in village_chunks:
            for village in chunk:
                attack_village_and_train_troops(village[1])
            # Wait before attacking the next set of 50 villages
            time.sleep(0.05)  # Adjust the sleep time as needed

# def get_villages_attack_and_train(uid, excluded_village_ids):
#     non_capital_villages = get_player_villages(uid, excluded_village_ids)
#     if non_capital_villages:
#         non_capital_villages.sort()  # Sort the list of villages in ascending order
#         for village in non_capital_villages:
#             attack_village_and_train_troops(village[1])
#             # Wait before attacking the next village
#             time.sleep(1)  # Adjust the sleep time as needed

# Function to get the list of villages for multiple players, attack random villages, and then train troops
def get_villages_attack_and_train_multi_uid(uid_list, excluded_village_ids):
    for uid in uid_list:
        non_capital_villages = get_player_villages(uid, excluded_village_ids)
        if non_capital_villages:
            random.shuffle(non_capital_villages)  # Shuffle the list of villages
            for village in non_capital_villages:  # Attack all villages in the shuffled list
                attack_village_and_train_troops(village[1])
            # Wait before attacking the next set of villages for the next player
            time.sleep(0.01)  # Adjust the sleep time as needed



# Function to switch to the 0000 village
def switch_to_0000_village():
    try:
        driver.get("https://fun.gotravspeed.com/village1.php?vid=5231")
        logging.info("Switched to the 0000 village")
    except Exception as e:
        logging.error(f"Error switching to the 0000 village: {e}")

# Main flow
initialize_driver()
check_internet_connection()
check_host()
accept_cookies()
login()

uids = [9, 10]

# Start the attacking thread
def attack_thread():
    while True:
        try:
            get_villages_attack_and_train_multi_uid(uids, excluded_village_ids)
        except Exception as e:
            logging.error(f"Error in attack thread: {e}")

# Start the training threads
def training_thread():
    while True:
        try:
            train_troops()
            time.sleep(0.5)
        except Exception as e:
            logging.error(f"Error in training thread: {e}")

# Create and start threads
attack_thread = threading.Thread(target=attack_thread)
training_threads = [threading.Thread(target=training_thread) for _ in range(9)]

attack_thread.start()
for t in training_threads:
    t.start()

# Wait for all threads to complete
attack_thread.join()
for t in training_threads:
    t.join()