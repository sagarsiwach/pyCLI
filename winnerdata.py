from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configuration
username = "SCAR"
password = "fiverr"

def login(driver):
    driver.get("https://gotravspeed.com")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name"))).send_keys(username)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(Keys.RETURN)

def extract_data(driver):
    with open("winners_data.tsv", "w", encoding="utf-8") as file:
        file.write("Round\tTimestamp\tName\tAlliance\tBest Attacker\tAttack Point\tBest Defender\tDefense Point\n")
        while True:
            # Wait for the table body to be present
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "winnerTbody")))
            # Re-find the rows on each iteration to avoid stale elements
            rows = driver.find_elements(By.CSS_SELECTOR, "#winnerTbody tr")
            for row in rows:
                columns = row.find_elements(By.TAG_NAME, "td")
                round_number = columns[0].text
                timestamp = columns[0].get_attribute("title").split(": ")[1]
                name = columns[1].text
                alliance = columns[2].text
                best_attacker = columns[3].text
                attack_point = columns[3].get_attribute("title").split(": ")[1]
                best_defender = columns[4].text
                defense_point = columns[4].get_attribute("title").split(": ")[1]
                file.write(f"{round_number}\t{timestamp}\t{name}\t{alliance}\t{best_attacker}\t{attack_point}\t{best_defender}\t{defense_point}\n")

            next_button = driver.find_element(By.CSS_SELECTOR, ".winner__pager-right")
            if "disabled" in next_button.get_attribute("class"):
                break
            next_button.click()
            # Wait for the new page to load
            time.sleep(1)




def main():
    options = webdriver.FirefoxOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Firefox(options=options)

    # Set zoom level to 50% and enter full screen
    driver.get("about:config")
    # driver.execute_script("document.body.style.zoom='50%'")
    driver.fullscreen_window()

    login(driver)

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Server Winners"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "select[name='server'] option[value='8']"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".profile__winner-button"))).click()

    extract_data(driver)

    driver.quit()

if __name__ == "__main__":
    main()
