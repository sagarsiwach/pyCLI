from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from concurrent.futures import ThreadPoolExecutor
import logging
import requests
import zapv2
from selenium.common.exceptions import TimeoutException
import json
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



# ZAP API configuration
zap_api_key = 'b6cfra7rpja4s33hd9kf0tfj7t'
zap_proxy = 'http://localhost:8080'
zap = zapv2.ZAPv2(apikey=zap_api_key, proxies={'http': zap_proxy, 'https': zap_proxy})
# Configuration
username = "SCAR"
password = "satkabir"
production_loops = 10
storage_loops = 50000
total_production_done = 0
total_storage_done = 0

# Setup Firefox options
options = Options()
options.headless = True

# Function to initialize WebDriver
def initialize_driver():
    global driver
    driver = webdriver.Firefox(options=options)

# Function to check internet connection
def check_internet_connection():
    while True:
        try:
            requests.get("https://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            print("No internet connection. Retrying...")
            time.sleep(5)

# Function to check host availability
def check_host():
    while True:
        try:
            response = requests.get("https://www.gotravspeed.com", timeout=5)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            print("Host error. Retrying...")
            time.sleep(5)

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

# Function to format numbers
def format_number(raw_number):
    try:
        number = float(raw_number.replace(',', ''))
        if number >= 1e24:
            formatted_number = f"{number / 1e24:.2f}Sui"
        elif number >= 1e21:
            formatted_number = f"{number / 1e21:.2f}S"
        elif number >= 1e18:
            formatted_number = f"{number / 1e18:.2f}Qui"
        elif number >= 1e15:
            formatted_number = f"{number / 1e15:.2f}Q"
        else:
            formatted_number = str(number)
        return formatted_number
    except ValueError:
        return raw_number

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
            print(f"Resource production increased: {total_production_done} done, {production_loops-i-1} remaining in this loop, {production_loops-total_production_done} total remaining. Speed: {speed:.2f} executions/minute")
            production_raw = driver.find_element(By.CLASS_NAME, "wood").get_attribute("title").split()[0]
            production_formatted = format_number(production_raw)
            print(f"Current production: {production_formatted}")
    except Exception as e:
        print("Error during production increase:", e)
        handle_error()








def increase_storage_and_production_optimized():
    global total_storage_done
    start_time = time.time()

    session = requests.Session()
    session.cookies.update({c['name']: c['value'] for c in driver.get_cookies()})

    def send_request(operation):
        global total_storage_done
        try:
            get_url = f"https://fun.gotravspeed.com/buy2.php?t={operation}"
            post_url = f"https://fun.gotravspeed.com/buy2.php?t={operation}&Shop=done"
            get_response = session.get(get_url)
            key = re.search(r'name="key" value="([^"]+)"', get_response.text).group(1)

            data = {
                'selected_res': '4',
                'xor': '100',
                'key': key
            }
            post_response = session.post(post_url, data=data, headers={"Referer": get_url})
            if post_response.status_code == 302:
                total_storage_done += 1
                logging.info(f"Operation {operation} increased: {total_storage_done} done.")
            else:
                logging.info(f"Error during operation {operation} increase: {post_response.status_code}")
        except Exception as e:
            logging.info(f"Error during operation {operation} increase:", e)

    operations = [0]  # Operation codes for resource and storage production
    for operation in operations:
        with ThreadPoolExecutor(max_workers=1) as executor:
            futures = [executor.submit(send_request, operation) for _ in range(100000)]
            for future in futures:
                future.result()

    elapsed_time = time.time() - start_time
    speed = total_storage_done / (elapsed_time / 60)
    logging.info(f"Total operations increased: {total_storage_done}, Speed: {speed:.2f} executions/minute")





























# def increase_storage_with_requests_concurrent():
#     global total_storage_done
#     start_time = time.time()

#     def send_storage_request(operation):
#         global total_storage_done
#         try:
#             get_url = f"https://fun.gotravspeed.com/buy2.php?t={operation}"
#             post_url = f"https://fun.gotravspeed.com/buy2.php?t={operation}&Shop=done"
#             get_response = requests.get(get_url, cookies=cookies)
#             key_start = get_response.text.find('name="key" value="') + len('name="key" value="')
#             key_end = get_response.text.find('"', key_start)
#             key = get_response.text[key_start:key_end]

#             data = {
#                 'selected_res': '4',
#                 'xor': '100',
#                 'key': key
#             }
#             post_response = requests.post(post_url, data=data, cookies=cookies, headers={"Referer": get_url})
#             if post_response.status_code == 302:
#                 total_storage_done += 1
#                 print(f"Storage increased: {total_storage_done} done.")
#             else:
#                 print(f"Error during storage increase: {post_response.status_code}")
#         except Exception as e:
#             print("Error during concurrent storage increase:", e)

#     cookies = {c['name']: c['value'] for c in driver.get_cookies()}

#     operations = [0, 2]  # Operation codes for resource and storage production
#     with ThreadPoolExecutor(max_workers=20) as executor:
#         for operation in operations:
#             futures = [executor.submit(send_storage_request, operation) for _ in range(storage_loops)]
#             for future in futures:
#                 future.result()

#     elapsed_time = time.time() - start_time
#     speed = total_storage_done / (elapsed_time / 60)
#     print(f"Total storage increased: {total_storage_done}, Speed: {speed:.2f} executions/minute")


















def increase_storage_with_requests():
    global total_storage_done
    start_time = time.time()
    try:
        get_url = "https://fun.gotravspeed.com/buy2.php?t=0"
        post_url = "https://fun.gotravspeed.com/buy2.php?t=0&Shop=done"
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}

        # Step 1: Make a GET request to retrieve the key
        get_response = requests.get(get_url, cookies=cookies)
        soup = BeautifulSoup(get_response.text, 'html.parser')
        key_input = soup.find('input', {'name': 'key'})
        if key_input:
            key = key_input['value']
        else:
            raise Exception("Key input not found in the response")

        # Step 2: Make a POST request with the retrieved key
        data = {
            'selected_res': '4',
            'xor': '100',
            'key': key
        }
        post_response = requests.post(post_url, data=data, cookies=cookies, headers={"Referer": get_url})
        if post_response.status_code == 302:
            total_storage_done += 1
            elapsed_time = time.time() - start_time
            speed = total_storage_done / (elapsed_time / 60)
            print(f"Storage increased: {total_storage_done} done, {storage_loops-i-1} remaining in this loop, {storage_loops-total_storage_done} total remaining. Speed: {speed:.2f} executions/minute")
        else:
            print(f"Error during storage increase: {post_response.status_code}")

    except Exception as e:
        print("Error during storage increase using requests:", e)
        handle_error()






















# Function to increase production
def increase_storage():
    global total_storage_done
    start_time = time.time()
    try:
        driver.get("https://fun.gotravspeed.com/buy2.php?t=2")
        for i in range(storage_loops):
            WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.NAME, "selected_res")))[3].click()
            driver.find_element(By.NAME, "xor").send_keys("100x")
            driver.find_element(By.ID, "sendbutton").click()
            driver.find_element(By.ID, "sendbutton").click()
            total_storage_done += 1
            elapsed_time = time.time() - start_time
            speed = total_storage_done / (elapsed_time / 60)
            print(f"Storage increased: {total_storage_done} done, {storage_loops-i-1} remaining in this loop, {storage_loops-total_storage_done} total remaining. Speed: {speed:.2f} executions/minute")
            storage = driver.find_element(By.CLASS_NAME, "ware").get_attribute("title")
            print(f"Current storage: {storage}")
            
    except Exception as e:
        print("Error during production increase:", e)
        handle_error()

# Function to increase storage
# def increase_storage():
#     global total_storage_done
#     start_time = time.time()
#     try:
#         get_url = "https://fun.gotravspeed.com/buy2.php?t=2"
#         post_url = "https://fun.gotravspeed.com/buy2.php?t=2&Shop=done"
#         cookies = {c['name']: c['value'] for c in driver.get_cookies()}
        
#         # Get the page to extract the dynamic key
#         get_response = requests.get(get_url, cookies=cookies)
#         soup = BeautifulSoup(get_response.text, 'html.parser')
#         key = soup.find('input', {'name': 'key'})['value']
        
#         headers = {
#             "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#             "accept-language": "en-US,en;q=0.9",
#             "cache-control": "max-age=0",
#             "content-type": "application/x-www-form-urlencoded",
#             "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
#             "sec-ch-ua-mobile": "?0",
#             "sec-ch-ua-platform": "\"Windows\"",
#             "sec-fetch-dest": "document",
#             "sec-fetch-mode": "navigate",
#             "sec-fetch-site": "same-origin",
#             "sec-fetch-user": "?1",
#             "upgrade-insecure-requests": "1"
#         }
#         data = f"selected_res=4&xor=100&key={key}"
        
#         for i in range(storage_loops):
#             response = requests.post(post_url, headers=headers, data=data, cookies=cookies)
#             if response.status_code == 200:
#                 total_storage_done += 1
#                 elapsed_time = time.time() - start_time
#                 speed = total_storage_done / (elapsed_time / 60)
#                 print(f"Storage increased: {total_storage_done} done, {storage_loops-i-1} remaining in this loop, {storage_loops-total_storage_done} total remaining. Speed: {speed:.2f} executions/minute")
#             else:
#                 print(f"Error during storage increase: {response.status_code}")
#     except Exception as e:
#         print("Error during storage increase:", e)
#         handle_error()

# def increase_storage_concurrently():
#     global total_storage_done

#     def send_storage_request(session, key):
#         global total_storage_done
#         data = {'selected_res': '4', 'xor': '100', 'key': key}
#         response = session.post(post_url, headers=headers, data=data)
#         if response.status_code == 200:
#             total_storage_done += 1
#             print(f"Storage increased: {total_storage_done} done.")
#         else:
#             print(f"Error during storage increase: {response.status_code}")

#     get_url = "https://fun.gotravspeed.com/buy2.php?t=2"
#     post_url = "https://fun.gotravspeed.com/buy2.php?t=2&Shop=done"

#     with requests.Session() as session:
#         # Load cookies from Selenium
#         for cookie in driver.get_cookies():
#             session.cookies.set(cookie['name'], cookie['value'])

#         # Get the page to extract the dynamic key
#         get_response = session.get(get_url)
#         soup = BeautifulSoup(get_response.text, 'html.parser')
#         key = soup.find('input', {'name': 'key'})['value']

#         headers = {
#             "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
#             "accept-language": "en-US,en;q=0.9",
#             "content-type": "application/x-www-form-urlencoded",
#             "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
#             "sec-ch-ua-mobile": "?0",
#             "sec-ch-ua-platform": "\"Windows\"",
#             "sec-fetch-dest": "document",
#             "sec-fetch-mode": "navigate",
#             "sec-fetch-site": "same-origin",
#             "sec-fetch-user": "?1",
#             "upgrade-insecure-requests": "1"
#         }

#         with ThreadPoolExecutor(max_workers=5) as executor:
#             for _ in range(storage_loops):
#                 executor.submit(send_storage_request, session, key)


# Function to get village links and sort them in ascending order
def get_village_links():
    village_links = driver.find_elements(By.XPATH, "//table[@id='vlist']//a[contains(@href, '?vid=')]")
    villages = [(link.get_attribute("href"), link.text) for link in village_links]
    sorted_villages = sorted(villages, key=lambda x: x[1])
    return [village[0] for village in sorted_villages]

# # Function to train Praetorians in the first village
# def train_praetorians():
#     try:
#         driver.get("https://fun.gotravspeed.com/build.php?id=25")
#         WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, "//tr[2]/td[3]/a"))).click()
#         driver.find_element(By.ID, "btn_train").click()
#         print("Training Praetorians in the current village.")
#     except Exception as e:
#         print(f"Error during Praetorians training in the current village: {e}")

# # Function to train tr2 in other villages
# def train_tr2():
#     try:
#         driver.get("https://fun.gotravspeed.com/build.php?id=25")
#         WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, "//tr[1]/td[3]/a"))).click()
#         driver.find_element(By.ID, "btn_train").click()
#         print("Training tr2 in the current village.")
#     except Exception as e:
#         print(f"Error during tr2 training in the current village: {e}")

# Function to train Praetorians in the first village
def train_praetorians_concurrently():
    def send_train_request():
        response = requests.post(url, headers=headers, data=praetorians_data, cookies=cookies)
        if response.status_code == 200:
            logging.info("Training Praetorians in the current village")
        else:
            logging.error(f"Error during Praetorians training: {response.status_code}")

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
        praetorians_data = "tf%5B22%5D=221117636153554570000&s1.x=50&s1.y=8"  # Change the troop ID and amount as needed
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(send_train_request) for _ in range(10)]
            for future in concurrent.futures.as_completed(futures):
                pass  # You can handle each future's result or exception here if needed

    except Exception as e:
        logging.error(f"Error during Praetorians training in the current village: {e}")

# Function to train tr2 in other villages
def train_tr2_concurrently():
    def send_train_request():
        response = requests.post(url, headers=headers, data=tr2_data, cookies=cookies)
        if response.status_code == 200:
            logging.info("Training tr2 in the current village")
        else:
            logging.error(f"Error during tr2 training: {response.status_code}")

    try:
        url = "https://fun.gotravspeed.com/build.php?id=25"
        tr2_data = "tf%5B24%5D=221117636153554570000&s1.x=50&s1.y=8"  # Change the troop ID and amount as needed
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(send_train_request) for _ in range(10)]
            for future in concurrent.futures.as_completed(futures):
                pass  # You can handle each future's result or exception here if needed

    except Exception as e:
        logging.error(f"Error during tr2 training in the current village: {e}")


# # Function to train troops in all villages
# def train_troops_in_all_villages():
#     village_urls = get_village_links()
#     for index, village_url in enumerate(village_urls):
#         driver.get(village_url)
#         time.sleep(1)
#         if index == 0:
#             for _ in range(10):
#                 train_praetorians()
#         else:
#             for _ in range(10):
#                 train_tr2()
        
        # Function to train troops in all villages concurrently
def train_troops_in_all_villages_concurrently():
    village_urls = get_village_links()

    for index, village_url in enumerate(village_urls):
        # Switch to the village
        driver.get(village_url)
        time.sleep(1)

        # Train Praetorians in the first village, tr2 in the others
        if index == 0:
            train_praetorians_concurrently()
        else:
            train_tr2_concurrently()

# Function to handle errors during execution
def handle_error():
    try:
        continue_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Continue')]")))
        continue_button.click()
    except Exception as e:
        print("Error handling failed, trying to re-login:", e)
        login()

# Main flow
initialize_driver()
check_internet_connection()
check_host()
accept_cookies()
login()

while True:
    try:
        # increase_production()
        # increase_storage()
        # increase_storage_with_requests()
        # increase_storage_with_requests_concurrent()
        increase_storage_and_production_optimized()
        # train_troops_in_all_villages_concurrently()
    except Exception as e:
        print(f"Error encountered: {e}. Reinitializing driver and checking connections before retrying.")
        driver.quit()  # Close the current driver instance
        initialize_driver()  # Reinitialize the driver
        check_internet_connection()
        check_host()
        login()
