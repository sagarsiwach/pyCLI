    with open('config.json', mode='r', encoding='utf-8') as file:
        config = json.load(file)
        print("Config keys:", config.keys())  # Debug print
        return config
