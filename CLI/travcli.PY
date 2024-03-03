import argparse
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_user_input():
    username = input("Enter your GoTravSpeed username: ")
    password = input("Enter your password: ")
    server = input("Enter the server (default is 'Fun'): ") or "Fun"
    return username, password, server.title()

def login(driver, username, password, server):
    driver.get("https://www.gotravspeed.com")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name"))).send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//h2/font[contains(text(),'{server}')]/ancestor::div[1]"))).click()
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'default__button-o-login')]"))).click()
    except TimeoutException:
        print("Already logged in or login button not found.")

def enable_build_mode(driver, server):
    server_url = server.lower()
    driver.get(f"https://{server_url}.gotravspeed.com/village2.php")
    try:
        build_mode_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='e_build']/a")))
        href_attribute = build_mode_button.get_attribute("href")
        if href_attribute and "BuildMode=0" in href_attribute:
            print("Build mode already enabled.")
        else:
            build_mode_button.click()
            print("Build mode enabled.")
    except TimeoutException:
        print("Build mode button not found.")

def upgrade_resource_fields(driver, server, max_level=30):
    server_url = server.lower()
    driver.get(f"https://{server_url}.gotravspeed.com/village1.php")
    resource_field_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    for field_id in resource_field_ids:
        try:
            field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//area[@href='build.php?id={field_id}']")))
            field.click()
            time.sleep(2)  # Wait for the upgrade to complete
            print(f"Resource field {field_id} upgraded.")
        except TimeoutException:
            print(f"Resource field {field_id} not found or already at max level.")

def main():
    parser = argparse.ArgumentParser(description='GoTravSpeed automation CLI.')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    args = parser.parse_args()

    username, password, server = get_user_input()

    options = Options()
    options.headless = args.headless
    driver = webdriver.Firefox(options=options)

    login(driver, username, password, server)
    enable_build_mode(driver, server)
    upgrade_resource_fields(driver, server)

    driver.quit()

if __name__ == "__main__":
    main()
