import httpx
import asyncio
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import requests


# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configuration
username = "SCAR"
password = "satkabir"
uid = 9  # User ID for attacking and training troops
uids = [9]
excluded_village_ids = ["9625"]
capital_uid = 9625

# Setup Firefox options
options = Options()
options.headless = True


# Function to initialize WebDriver
def initialize_driver():
    global driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(
        "--no-sandbox"
    )  # This line is important for running on a server
    chrome_options.add_argument(
        "--disable-dev-shm-usage"
    )  # This line is important for running in a Docker container or on a server
    driver = webdriver.Chrome(options=chrome_options)
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
            response = requests.get("https://www.gotravspeed.com", timeout=2)
            if response.status_code == 200:
                logging.info("Host is available")
                return True
        except requests.RequestException:
            logging.warning("Host error. Retrying...")
            time.sleep(1)


# Function to accept cookies
def accept_cookies():
    try:
        WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.ID, "cookie__btn"))
        ).click()
        logging.info("Cookies accepted")
    except Exception as e:
        logging.error(f"Error accepting cookies: {e}")


# Function to log in
def login():
    while True:
        try:
            driver.get("https://www.gotravspeed.com")
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.ID, "name"))
            ).send_keys(username)
            driver.find_element(By.ID, "password").send_keys(password)
            driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
            WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//h2/font[contains(text(),'Fun')]/ancestor::div[1]")
                )
            ).click()
            WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class,'default__button-o-login')]")
                )
            ).click()
            return
        except Exception as e:
            print("Error during login:", e)
            check_internet_connection()
            check_host()


# Function to get the list of non-capital villages for a given player, excluding specified village IDs
def get_player_villages(uid, excluded_village_ids):
    try:
        driver.get(f"https://fun.gotravspeed.com/profile.php?uid={uid}")
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.ID, "villages"))
        )
        village_links = driver.find_elements(
            By.XPATH, "//table[@id='villages']//a[contains(@href, 'village3.php?id=')]"
        )
        villages = []
        for link in village_links:
            village_id = link.get_attribute("href").split("=")[-1]
            if village_id not in excluded_village_ids:
                village_name = link.text
                village_url = f"https://fun.gotravspeed.com/v2v.php?id={village_id}"
                villages.append((village_name, village_url))
        sorted_villages = sorted(villages, key=lambda x: x[0])
        logging.info(
            f"Found {len(sorted_villages)} non-capital villages for player {uid} excluding village IDs {excluded_village_ids}"
        )
        return sorted_villages
    except Exception as e:
        logging.error(
            f"Error getting non-capital villages for player {uid} excluding village IDs {excluded_village_ids}: {e}"
        )


# Function to attack a village (synchronous, using Selenium)
def attack_village(village_url):
    try:
        driver.get(village_url)
        # Add your attack logic here
        logging.info(f"Attacked village: {village_url}")
    except Exception as e:
        logging.error(f"Error attacking village {village_url}: {e}")


# Function to train troops asynchronously
async def train_troops_async(client, url, headers, data, cookies):
    try:
        async with client.post(
            url, headers=headers, data=data, cookies=cookies
        ) as response:
            if response.status_code == 200:
                logging.info("Training Praetorians in the current village")
            else:
                logging.error(
                    f"Error during Praetorians training: {response.status_code}"
                )
    except Exception as e:
        logging.error(f"Error during Praetorians training in the current village: {e}")


# Function to perform multiple asynchronous training operations
async def perform_training(village_url, num_trainings, batch_size, num_batches):
    async with httpx.AsyncClient() as client:
        # Extract cookies from Selenium
        cookies = {c["name"]: c["value"] for c in driver.get_cookies()}

        # Prepare headers and data for the training request
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }
        data = "tf%5B6%5D=1000000000000000000000&s1.x=50&s1.y=8"

        # Run the training tasks in batches
        for _ in range(num_batches):
            # Create a list of training tasks for the current batch
            tasks = [
                train_troops_async(client, village_url, headers, data, cookies)
                for _ in range(batch_size)
            ]

            # Run the training tasks concurrently
            await asyncio.gather(*tasks)

            # Optional: sleep between batches to prevent rate limiting
            await asyncio.sleep(random.uniform(0.1, 0.5))


# Main flow with asynchronous troop training
async def main():
    initialize_driver()
    check_internet_connection()
    check_host()
    accept_cookies()
    login()

    for uid in uids:
        non_capital_villages = get_player_villages(uid, excluded_village_ids)
        if non_capital_villages:
            random.shuffle(non_capital_villages)  # Shuffle the list of villages
            for village in non_capital_villages:
                # Perform asynchronous troop training with 12 requests at once, repeated 10 times
                await perform_training(village[1], num_trainings=70, batch_size=12, num_batches=10)

                # Attack village once
                attack_village(village[1])

                # Optional: sleep between operations to mimic human-like intervals and prevent rate limiting
                await asyncio.sleep(
                    random.uniform(0.1, 0.5)
                )  # Random sleep between operations
