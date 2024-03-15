import csv
import logging
import time
import httpx
from bs4 import BeautifulSoup
from config import read_config
from login import login

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Read configuration from CSV
config = read_config()

async def rename_village(village_id, new_name, cookies):
    async with httpx.AsyncClient(cookies=cookies) as client:
        # Get the profile page for the village to retrieve the form data
        response = await client.get(f"https://fun.gotravspeed.com/profile.php?vid={village_id}&t=1")
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find the current village name and other form data
        current_name = soup.find('input', {'name': 'dname'})['value']
        form_data = {
            'e': '1',
            'oldavatar': soup.find('input', {'name': 'oldavatar'})['value'],
            'jahr': '',
            'monat': '0',
            'tag': '',
            'be1': '',
            'mw': '0',
            'ort': '',
            'dname': new_name,
            'be2': '',
            's1.x': '25',
            's1.y': '1'
        }
        # Send a POST request to update the village name
        await client.post(f"https://fun.gotravspeed.com/profile.php?vid={village_id}", data=form_data)
        logging.info(f"Renamed village {current_name} (ID: {village_id}) to {new_name}")

async def rename_all_villages(cookies, new_name_pattern):
    async with httpx.AsyncClient(cookies=cookies) as client:
        # Get the list of villages from the profile page
        response = await client.get("https://fun.gotravspeed.com/profile.php?t=1")
        soup = BeautifulSoup(response.text, 'html.parser')
        villages = soup.find_all('a', href=lambda href: href and 'profile.php?vid=' in href)
        # Rename each village
        for i, village in enumerate(villages, start=1):
            village_id = village['href'].split('=')[-1]
            new_name = new_name_pattern.format(i)
            await rename_village(village_id, new_name, cookies)

# Example usage
async def main():
    cookies = await login()  # Assuming you have a login function
    await rename_all_villages(cookies, new_name_pattern="Village {:04}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
