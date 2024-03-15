import csv
import logging
import time
import httpx
from bs4 import BeautifulSoup
from config import read_config
from login import login
from httpx._config import DEFAULT_TIMEOUT_CONFIG

# Setup logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# URLs
BASE_URL = "https://fun.gotravspeed.com"
BUILD_URL_TEMPLATE = BASE_URL + "/build.php?id={}"
VILLAGE3_URL_TEMPLATE = BASE_URL + "/village3.php?id={}"
V2V_URL = BASE_URL + "/v2v.php"
SHOWVILL_URL = BASE_URL + "/shownvill.php"

# Replace with your actual credentials
USERNAME = "your_username"
PASSWORD = "your_password"

async def login(client):
    # Placeholder login function
    # You need to implement actual login logic here, which might include:
    # - Navigating to the login page
    # - Submitting the login form with your credentials
    # - Handling any redirects or additional authentication steps
    logging.info("Logged in with placeholder function")

def generate_spiral_village_ids(center_id, start_radius, max_radius):
    ids = []
    for radius in range(start_radius, max_radius + 1):
        for i in range(-radius, radius + 1):
            ids.append(center_id - 401 * radius + i)
        for i in range(-radius + 1, radius):
            ids.append(center_id - 401 * i + radius)
        for i in range(-radius, radius + 1):
            ids.append(center_id + 401 * radius - i)
        for i in range(-radius + 1, radius):
            ids.append(center_id + 401 * i - radius)
    return ids

async def train_settlers(client, village_info):
    building_id = village_info['ID for Settler Training Position / Building']
    data = {
        'tf[{}]'.format(village_info['Settler TF ID']): '3',
        's1.x': '60',
        's1.y': '7'
    }
    await client.post(BUILD_URL_TEMPLATE.format(building_id), data=data)
    logging.info("Training settlers initiated")

async def find_and_settle_new_village(client, center_id, start_radius, max_radius):
    spiral_village_ids = generate_spiral_village_ids(center_id, start_radius, max_radius)
    for village_id in spiral_village_ids:
        response = await client.get(VILLAGE3_URL_TEMPLATE.format(village_id))
        if '»building a new village' in response.text:
            soup = BeautifulSoup(response.text, 'html.parser')
            key = soup.find('input', {'name': 'key'})['value']
            data = {
                'id': village_id,
                'c': 4,
                't[1]': 0, 't[2]': 0, 't[3]': 0, 't[4]': 0, 't[5]': 0,
                't[6]': 0, 't[7]': 0, 't[8]': 0, 't[9]': 0, 't[10]': 3,
                'key': key
            }
            await client.post(V2V_URL, data=data)
            logging.info(f"New village settled at {village_id}")
            break

async def main():
    async with httpx.AsyncClient() as client:
        await login(client)  # Implement the login logic
        village_info = {
            'ID for Settler Training Position / Building': '29',  # Example value
            'Settler TF ID': '10'  # Example value
        }
        await train_settlers(client, village_info)
        await find_and_settle_new_village(client, center_id=12345, start_radius=1, max_radius=25)

if __name__ == "__main__":
    asyncio.run(main())






import asyncio
import csv
import httpx
from bs4 import BeautifulSoup
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# URLs
BASE_URL = "https://fun.gotravspeed.com"
BUILD_URL_TEMPLATE = BASE_URL + "/build.php?id={building_id}"
VILLAGE3_URL_TEMPLATE = BASE_URL + "/village3.php?id={village_id}"
V2V_URL = BASE_URL + "/v2v.php"
SHOWVILL_URL = BASE_URL + "/shownvill.php"

# CSV Paths
VILLAGE_INFO_CSV = "village_info.csv"
BUILDING_SEQUENCE_CSV = "buildingsequence.csv"

async def read_csv(filepath):
    with open(filepath, mode='r') as file:
        reader = csv.DictReader(file)
        return list(reader)


async def train_settlers(client, village_info):
    building_id = village_info['ID for Settler Training Position / Building']
    url = BUILD_URL_TEMPLATE.format(building_id=building_id)
    # The POST data for training settlers should be fetched or constructed
    data = {
        'tf[10]': '3',
        's1.x': '60',
        's1.y': '7'
    }
    await client.post(url, data=data)
    logging.info("Training settlers initiated")

async def find_and_settle_new_village(client, village_info):
    start_radius = int(village_info['Start Radius'])
    end_radius = int(village_info['End Radius'])
    # Implement spiral logic here to generate village IDs around the center village
    # For simplicity, we're using a placeholder list of village IDs
    potential_village_ids = [12345]  # Placeholder

    for village_id in potential_village_ids:
        response = await client.get(VILLAGE3_URL_TEMPLATE.format(village_id=village_id))
        if '»building a new village' in response.text:
            soup = BeautifulSoup(response.text, 'html.parser')
            key = soup.find('input', {'name': 'key'})['value']
            data = {
                'id': village_id,
                'c': 4,
                't[1]': 0, 't[2]': 0, 't[3]': 0, 't[4]': 0, 't[5]': 0,
                't[6]': 0, 't[7]': 0, 't[8]': 0, 't[9]': 0, 't[10]': 3,
                'key': key
            }
            await client.post(V2V_URL, data=data)
            logging.info(f"New village settled at {village_id}")
            break

async def main():
    # Read CSVs
    village_info_list = await read_csv(VILLAGE_INFO_CSV)
    building_sequence = await read_csv(BUILDING_SEQUENCE_CSV)

    # Use httpx.AsyncClient as a context manager to ensure proper cleanup
    async with httpx.AsyncClient() as client:
        # Login
        await login(client, "your_username", "your_password")

        # Train settlers in the first village
        await train_settlers(client, village_info_list[0])

        # Find and settle a new village
        await find_and_settle_new_village(client, village_info_list[0])

if __name__ == "__main__":
    asyncio.run(main())
