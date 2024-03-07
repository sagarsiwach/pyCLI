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
storage_loops = 0
total_production_done = 0
total_storage_done = 0

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
    global total_production_done
    current_loop = 'production'
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

def increase_storage():
    global total_storage_done
    current_loop = 'storage'
    start_time = time.time()
    try:
        driver.get("https://fun.gotravspeed.com/buy2.php?t=2")
        for i in range(storage_loops):
            WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.NAME, "selected_res")))[3].click()
            driver.find_element(By.NAME, "xor").send_keys("100x")
            driver.find_element(By.ID, "sendbutton").click()
            total_storage_done += 1
            elapsed_time = time.time() - start_time
            speed = total_storage_done / (elapsed_time / 60)
            print(f"Storage increased: {total_storage_done} done, {storage_loops-i-1} remaining in this loop, {storage_loops-total_storage_done} total remaining. Speed: {speed:.2f} executions/minute")
            storage = driver.find_element(By.CLASS_NAME, "ware").get_attribute("title")
            print(f"Current storage: {storage}")
    except Exception as e:
        print("Error during storage increase:", e)
        handle_error()

def get_village_links():
    village_links = driver.find_elements(By.XPATH, "//table[@id='vlist']//a[contains(@href, '?vid=')]")
    villages = [(link.get_attribute("href"), link.text) for link in village_links]
    sorted_villages = sorted(villages, key=lambda x: x[1])
    return [village[0] for village in sorted_villages]

def train_praetorians():
    try:
        driver.get("https://fun.gotravspeed.com/build.php?id=25")
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, "//tr[2]/td[3]/a"))).click()
        driver.find_element(By.ID, "btn_train").click()
        print("Training Praetorians in the current village.")
    except Exception as e:
        print(f"Error during Praetorians training in the current village: {e}")

def train_tr2():
    try:
        driver.get("https://fun.gotravspeed.com/build.php?id=25")
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, "//tr[1]/td[3]/a"))).click()
        driver.find_element(By.ID, "btn_train").click()
        print("Training tr2 in the current village.")
    except Exception as e:
        print(f"Error during tr2 training in the current village: {e}")

def train_troops_in_all_villages():
    village_urls = get_village_links()
    for index, village_url in enumerate(village_urls):
        driver.get(village_url)
        time.sleep(1)
        if index == 0:
            for _ in range(10):
                train_praetorians()
        else:
            for _ in range(10):
                train_tr2()

def return_to_capital():
    village_urls = get_village_links()
    if village_urls:
        driver.get(village_urls[0])

def handle_error():
    try:
        continue_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Continue')]")))
        continue_button.click()
    except Exception as e:
        print("Error handling failed, trying to re-login:", e)
        login()

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


# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time

# # Configuration
# username = "SCAR"
# password = "fiverr"
# production_loops = 62500
# storage_loops = 0
# total_production_done = 0
# total_storage_done = 0

# # Setup Firefox options
# options = Options()
# options.headless = True

# # Initialize WebDriver
# driver = webdriver.Firefox(options=options)

# def accept_cookies():
#     try:
#         WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "cookie__btn"))).click()
#     except Exception as e:
#         print("Error accepting cookies:", e)

# def login():
#     try:
#         driver.get("https://www.gotravspeed.com")
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name"))).send_keys(username)
#         driver.find_element(By.ID, "password").send_keys(password)
#         driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
#         WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//h2/font[contains(text(),'Fun')]/ancestor::div[1]"))).click()
#         WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'default__button-o-login')]"))).click()
#     except Exception as e:
#         print("Error during login:", e)
#         driver.quit()
# def format_number(raw_number):
#     try:
#         number = float(raw_number.replace(',', ''))
#         if number >= 1e24:
#             formatted_number = f"{number / 1e24:.2f}Sui"
#         elif number >= 1e21:
#             formatted_number = f"{number / 1e21:.2f}S"
#         elif number >= 1e18:
#             formatted_number = f"{number / 1e18:.2f}Qui"
#         elif number >= 1e15:
#             formatted_number = f"{number / 1e15:.2f}N"
#         elif number >= 1e12:
#             formatted_number = f"{number / 1e12:.2f}Q"
#         elif number >= 1e9:
#             formatted_number = f"{number / 1e9:.2f}T"
#         elif number >= 1e6:
#             formatted_number = f"{number / 1e6:.2f}B"
#         elif number >= 1e3:
#             formatted_number = f"{number / 1e3:.2f}M"
#         else:
#             formatted_number = str(number)
#         return formatted_number
#     except ValueError:
#         return raw_number

# def increase_production():
#     global total_production_done
#     current_loop = 'production'
#     start_time = time.time()
#     try:
#         driver.get("https://fun.gotravspeed.com/buy2.php?t=0")
#         for i in range(production_loops):
#             WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.NAME, "selected_res")))[3].click()
#             driver.find_element(By.NAME, "xor").send_keys("100x")
#             driver.find_element(By.ID, "sendbutton").click()
#             total_production_done += 1
#             elapsed_time = time.time() - start_time
#             speed = total_production_done / (elapsed_time / 60)
#             print(f"Resource production increased: {total_production_done} done, {production_loops-i-1} remaining in this loop, {production_loops-total_production_done} total remaining. Speed: {speed:.2f} executions/minute")
#             production_raw = driver.find_element(By.CLASS_NAME, "wood").get_attribute("title").split()[0]
#             production_formatted = format_number(production_raw)
#             print(f"Current production: {production_formatted}")
            
#     except Exception as e:
#         print("Error during production increase:", e)
#         login()

# def increase_storage():
#     global total_storage_done
#     current_loop = 'storage'
#     start_time = time.time()
#     try:
#         driver.get("https://fun.gotravspeed.com/buy2.php?t=2")
#         for i in range(storage_loops):
#             WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.NAME, "selected_res")))[3].click()
#             driver.find_element(By.NAME, "xor").send_keys("100x")
#             driver.find_element(By.ID, "sendbutton").click()
#             total_storage_done += 1
#             elapsed_time = time.time() - start_time
#             speed = total_storage_done / (elapsed_time / 60)
#             print(f"Storage increased: {total_storage_done} done, {storage_loops-i-1} remaining in this loop, {storage_loops-total_storage_done} total remaining. Speed: {speed:.2f} executions/minute")
#             storage = driver.find_element(By.CLASS_NAME, "ware").get_attribute("title")
#             print(f"Current storage: {storage}")
#     except Exception as e:
#         print("Error during storage increase:", e)
#         login()





# # def increase_production():
# #     global total_production_done
# #     start_time = time.time()
# #     try:
# #         driver.get("https://fun.gotravspeed.com/buy2.php?t=0")
# #         for i in range(production_loops):
# #             WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.NAME, "selected_res")))[3].click()
# #             driver.find_element(By.NAME, "xor").send_keys("100x")
# #             driver.find_element(By.ID, "sendbutton").click()
# #             total_production_done += 1
# #             elapsed_time = time.time() - start_time
# #             speed = total_production_done / (elapsed_time / 60)
# #             print(f"Resource production increased: {total_production_done} done, {production_loops-i-1} remaining in this loop, {production_loops-total_production_done} total remaining. Speed: {speed:.2f} executions/minute")
# #     except Exception as e:
# #         print("Error during production increase:", e)
# #         login()

# # def increase_storage():
# #     global total_storage_done
# #     start_time = time.time()
# #     try:
# #         driver.get("https://fun.gotravspeed.com/buy2.php?t=2")
# #         for i in range(storage_loops):
# #             WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.NAME, "selected_res")))[3].click()
# #             driver.find_element(By.NAME, "xor").send_keys("100x")
# #             driver.find_element(By.ID, "sendbutton").click()
# #             total_storage_done += 1
# #             elapsed_time = time.time() - start_time
# #             speed = total_storage_done / (elapsed_time / 60)
# #             print(f"Storage increased: {total_storage_done} done, {storage_loops-i-1} remaining in this loop, {storage_loops-total_storage_done} total remaining. Speed: {speed:.2f} executions/minute")
# #     except Exception as e:
# #         print("Error during storage increase:", e)
# #         login()

# def get_village_links():
#     village_links = driver.find_elements(By.XPATH, "//table[@id='vlist']//a[contains(@href, '?vid=')]")
#     # Extract the URLs and village names for each village
#     villages = [(link.get_attribute("href"), link.text) for link in village_links]
#     # Sort the villages based on the village name
#     sorted_villages = sorted(villages, key=lambda x: x[1])
#     # Return only the URLs, in sorted order
#     return [village[0] for village in sorted_villages]


# def train_praetorians():
#     try:
#         driver.get("https://fun.gotravspeed.com/build.php?id=25")
#         WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//tr[2]/td[3]/a"))).click()
#         driver.find_element(By.ID, "btn_train").click()
#         print("Training Praetorians in the current village.")
#     except Exception as e:
#         print(f"Error during Praetorians training in the current village: {e}")

# def train_tr2():
#     try:
#         driver.get("https://fun.gotravspeed.com/build.php?id=25")
#         WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//tr[2]/td[3]/a"))).click()
#         driver.find_element(By.ID, "btn_train").click()
#         print("Training tr2 in the current village.")
#     except Exception as e:
#         print(f"Error during tr2 training in the current village: {e}")

# def train_troops_in_all_villages():
#     village_urls = get_village_links()
#     for index, village_url in enumerate(village_urls):
#         driver.get(village_url)
#         time.sleep(2)
#         if index == 0:
#             for _ in range(15):
#                 train_praetorians()
#         else:
#             for _ in range(15):
#                 train_tr2()

# def return_to_capital():
#     village_urls = get_village_links()
#     if village_urls:
#         driver.get(village_urls[0])

# # Main flow
# accept_cookies()
# login()

# while True:
#     try:
#         increase_production()
#         increase_storage()
#         # train_troops_in_all_villages()
#     except Exception as e:
#         print(f"Error encountered: {e}. Restarting from login page.")
#         login()
