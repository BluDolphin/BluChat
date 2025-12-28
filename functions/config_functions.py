import json

# Config is dictionary based 
# Location is a nested dictionary with city (str), region (str), and country (str) keys
# Each AI config is a nested dictionary with usable (bool), api_key (str), and model (str) keys

def initialise_config(location_data):
    # Define default models for each LLM
    # These can be changed later via settings page
    # These are set as the lastest methods available as of December 2025
    gemini_default_model = 'gemini-flash-latest'
    mistral_default_model = 'mistral-small-latest'
    chatgpt_default_model = 'gpt-5-mini'
    deepseek_default_model = 'deepseek-chat'
    claude_default_model = 'claude-haiku-4.5'
    
    
    default_config = {
        'whitelist_toggle': False,
        'country_code': '',
        'modem_interface': '/dev/ttyAMD1',
        'location': location_data,
        'prompt_instructions': '',
        'active_llm': '',
        'llm_configs': {
            'gemini_config': {'usable': False, 'api_key': '', 'model': gemini_default_model},
            'mistral_config': {'usable': False, 'api_key': '', 'model': mistral_default_model},
            'chatgpt_config': {'usable': False, 'api_key': '', 'model': chatgpt_default_model},
            'deepseek_config': {'usable': False, 'api_key': '', 'model': deepseek_default_model}, 
            'claude_config': {'usable': False, 'api_key': '', 'model': claude_default_model}
        }

    }
    
    with open('data/config.json', 'w') as f:
        json.dump(default_config, f, indent=4)
        
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
        json.dump(stored_data, f, indent=4)
    
    return stored_data
