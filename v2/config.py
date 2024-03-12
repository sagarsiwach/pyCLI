import csv

def read_config():
    with open('config.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)  # Specify the delimiter as a tab
        config = next(reader)
        print("Config keys:", config.keys())  # Debug print
        return config

