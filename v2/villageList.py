import csv
import httpx
from bs4 import BeautifulSoup
from login import login
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def get_village_ids_and_write_info_to_csv(cookies):
    url = "https://fun.gotravspeed.com/profile.php?uid=15"
    async with httpx.AsyncClient(cookies=cookies) as client:
        response = await client.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        village_links = soup.find_all('a', href=lambda href: href and 'village3.php?id=' in href)
        village_ids = [link['href'].split('=')[-1] for link in village_links]

        # Define the header for the CSV file
        header = [
            'ID for Settler Training Position / Building',
            'Settler TF ID',
            'Village IDs',
            'Village Names',
            'Village Type',
            'Start Radius',
            'End Radius',
            'Villages Number'
        ]

        # Write the data to CSV
        with open('village_info.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            for i, vid in enumerate(village_ids, start=0):
                if i == 0:
                    # Special values for the first row
                    village_name = "0000"
                    start_radius = 1
                    end_radius = 25
                    villages_number = 300
                else:
                    village_name = f"{i:04}"
                    start_radius = 'Unknown'
                    end_radius = 'Unknown'
                    villages_number = 'Unknown'

                village_type = 'capital' if i == 0 else ('artefact' if i <= 10 else 'farm')
                writer.writerow([
                    30 if i == 0 else 'Unknown',  # ID for Settler Training Position / Building
                    10 if i == 0 else 'Unknown',  # Settler TF ID
                    vid,
                    village_name,
                    village_type,
                    start_radius,
                    end_radius,
                    villages_number
                ])

        logging.info(f"Village IDs and info written to CSV: {village_ids}")
        return village_ids

# Example usage
async def main():
    cookies = await login()
    village_ids = await get_village_ids_and_write_info_to_csv(cookies)
    print(village_ids)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
