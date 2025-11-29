import json

def initialise_config():
    default_config = {
        "whitelist_toggle": False,
        "country_code": ""
    }
    
    with open('data/config.json', 'w') as f:
        json.dump(default_config, f)
        
def load_all_config():
    with open('data/config.json') as f:
        stored_data = json.load(f)
    
    return stored_data

def get_config(request):
    with open('data/config.json') as f:
        stored_data = json.load(f)
    
    return stored_data[request]

def update_config(request, data):
    with open('data/config.json', 'r') as f:
        stored_data = json.load(f)
    
    # Update the configuration with the new data
    stored_data[request] = data
    
    with open('data/config.json', 'w') as f:
        json.dump(stored_data, f)
    

