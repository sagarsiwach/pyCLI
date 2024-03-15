import csv
import logging
import asyncio
from login import login
import httpx
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def build_building(cookies, position_id, building_id, building_name):
    logging.info(f"Attempting to build/upgrade {building_name} at position {position_id}")
    url = f"https://fun.gotravspeed.com/build.php?id={position_id}&gid={building_id}"
    async with httpx.AsyncClient(cookies=cookies, timeout=30.0) as client:
        # Fetch CSRF token for building
        pre_response = await client.get(url)
        if pre_response.status_code == 200:
            soup = BeautifulSoup(pre_response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': 'a'})['value']
            # Build/upgrade the building
            build_response = await client.get(f"{url}&a={csrf_token}")
            if build_response.status_code == 200:
                logging.info(f"Successfully built/upgraded {building_name} at position {position_id}")
            else:
                logging.error(f"Failed to build/upgrade {building_name} at position {position_id}. Status code: {build_response.status_code}")
        else:
            logging.error(f"Failed to fetch CSRF token for {building_name} at position {position_id}")

async def execute_building_sequence(cookies, village_type="capital"):
    with open('buildingsequence.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            position_id = row[f"{village_type}PositionID"]
            building_id = row[f"{village_type}BuildingID"]
            loop = int(row[f"{village_type}Loop"])
            building_name = f"{village_type} Building"
            if position_id and building_id:  # Check if position_id and building_id are not empty
                await build_building(cookies, position_id, building_id, building_name)
                for _ in range(loop-1):
                    await build_building(cookies, position_id, building_id, building_name)  # Assuming additional loops imply upgrading

async def main():
    cookies = await login()
    # Example usage for capital village building sequence
    await execute_building_sequence(cookies, village_type="capital")
    # Add calls for secondary and artifact villages if needed

if __name__ == "__main__":
    asyncio.run(main())
