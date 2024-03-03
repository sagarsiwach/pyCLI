from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configuration
username = "SCAR"
password = "fiverr"
production_loops = 500
storage_loops = 500
total_production_done = 0
total_storage_done = 0
# troop_training_toggle = True  # True for Praetorians, False for Equites Caesaris
# train_interval = 30  # Train troops every 30 seconds
# enable_troop_training = True  # Toggle for enabling/disabling troop training
# current_loop = None  # Can be 'production' or 'storage'
# loops_since_last_training = 0



# Setup Firefox options
options = Options()
options.headless = True

# Initialize WebDriver
driver = webdriver.Firefox(options=options)

def accept_cookies():
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "cookie__btn"))).click()
    except Exception as e:
        print("Error accepting cookies:", e)

def login():
    try:
        driver.get("https://www.gotravspeed.com")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name"))).send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//h2/font[contains(text(),'Fun')]/ancestor::div[1]"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'default__button-o-login')]"))).click()
    except Exception as e:
        print("Error during login:", e)
        driver.quit()

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
            formatted_number = f"{number / 1e15:.2f}N"
        elif number >= 1e12:
            formatted_number = f"{number / 1e12:.2f}Q"
        elif number >= 1e9:
            formatted_number = f"{number / 1e9:.2f}T"
        elif number >= 1e6:
            formatted_number = f"{number / 1e6:.2f}B"
        elif number >= 1e3:
            formatted_number = f"{number / 1e3:.2f}M"
        else:
            formatted_number = str(number)
        return formatted_number
    except ValueError:
        return raw_number

def increase_production():
    global total_production_done, current_loop
    current_loop = 'production'
    start_time = time.time()
    try:
        driver.get("https://fun.gotravspeed.com/buy2.php?t=0")
        for i in range(production_loops):
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.NAME, "selected_res")))[3].click()
            driver.find_element(By.NAME, "xor").send_keys("100x")
            driver.find_element(By.ID, "sendbutton").click()
            total_production_done += 1
            elapsed_time = time.time() - start_time
            speed = total_production_done / (elapsed_time / 60)
            print(f"Resource production increased: {total_production_done} done, {production_loops-i-1} remaining in this loop, {production_loops-total_production_done} total remaining. Speed: {speed:.2f} executions/minute")
            production_raw = driver.find_element(By.CLASS_NAME, "wood").get_attribute("title").split()[0]
            production_formatted = format_number(production_raw)
            print(f"Current production: {production_formatted}")
            # loops_since_last_training += 1
            # if enable_troop_training and loops_since_last_training >= 30:
            #     train_troops()
            #     loops_since_last_training = 0  # Reset the counter
    except Exception as e:
        print("Error during production increase:", e)
        login()

def increase_storage():
    global total_storage_done, current_loop 
    current_loop = 'storage'
    start_time = time.time()
    try:
        driver.get("https://fun.gotravspeed.com/buy2.php?t=2")
        for i in range(storage_loops):
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.NAME, "selected_res")))[3].click()
            driver.find_element(By.NAME, "xor").send_keys("100x")
            driver.find_element(By.ID, "sendbutton").click()
            total_storage_done += 1
            elapsed_time = time.time() - start_time
            speed = total_storage_done / (elapsed_time / 60)
            print(f"Storage increased: {total_storage_done} done, {storage_loops-i-1} remaining in this loop, {storage_loops-total_storage_done} total remaining. Speed: {speed:.2f} executions/minute")
            storage = driver.find_element(By.CLASS_NAME, "ware").get_attribute("title")
            print(f"Current storage: {storage}")
            # loops_since_last_training += 1
            # if enable_troop_training and loops_since_last_training >= 30:
            #     train_troops()
            #     loops_since_last_training = 0  # Reset the counter
    except Exception as e:
        print("Error during storage increase:", e)
        login()

def get_village_links():
    # Find all village links in the right sidebar
    village_links = driver.find_elements(By.XPATH, "//table[@id='vlist']//a[contains(@href, '?vid=')]")
    # Extract the URLs for each village
    village_urls = [link.get_attribute("href") for link in village_links]
    return village_urls

def train_praetorians():
    try:
        # Navigate to the barracks
        driver.get("https://fun.gotravspeed.com/build.php?id=25")
        # Wait for the max button to be visible and click it
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//tr[1]/td[3]/a"))).click()
        # Click the train button
        driver.find_element(By.ID, "btn_train").click()
        print("Training Praetorians in the current village.")
    except Exception as e:
        print(f"Error during Praetorians training in the current village: {e}")

def train_troops_in_all_villages():
    return_to_capital()
    village_urls = get_village_links()
    for village_url in village_urls:
        # Switch to the village
        driver.get(village_url)
        # Wait for the village to load (e.g., wait for the barracks to be visible)
        time.sleep(2)
        # Train Praetorians in this village
        for _ in range(15):
            train_praetorians()

def return_to_capital():
    village_urls = get_village_links()
    if village_urls:
        # Assuming the first village in the list is the capital
        driver.get(village_urls[0])

# Main flow
accept_cookies()
login()

while True:
    try:
        increase_production()
        increase_storage()
        train_troops_in_all_villages()
    except Exception as e:
        print(f"Error encountered: {e}. Restarting from login page.")
        login()
