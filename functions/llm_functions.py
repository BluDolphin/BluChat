from datetime import datetime

from functions.config_functions import get_config, update_config
from functions.encryption_functions import decrypt_data, encrypt_data

# Return 0 for okay
# Return 1 for error
# test_config is a tuple of (api_key, model) for testing validity without updating stored config
def check_llm_config(llm_name, encryption_key, test_config=None):   
    if llm_name == 'gemini':
        response = gemini_call('test', '', encryption_key, test_config=test_config) # Test call to check validity
        
        if isinstance(response, tuple): # If error returned
            update_llm_usability(llm_name, False) # Update usability status to False
            return response # Return error code and message
        
        update_llm_usability(llm_name, True) # Update usability status to True
        return 0 # Return successful response
    
    elif llm_name == 'mistral':
        response = mistral_call('test', '', encryption_key, test_config=test_config) # Test call to check validity
        if isinstance(response, tuple): # If error returned
            update_llm_usability(llm_name, False) # Update usability status to False
            return response # Return error code and message
        
        update_llm_usability(llm_name, True) # Update usability status to True
        return 0 # Return successful response
    
    elif llm_name == 'chatgpt':
        response = chatgpt_call('test', '', encryption_key, test_config=test_config) # Test call to check validity
        if isinstance(response, tuple): # If error returned
            update_llm_usability(llm_name, False) # Update usability status to False
            return response # Return error code and message
        
        update_llm_usability(llm_name, True) # Update usability status to True
        return 0 # Return successful response
    
    elif llm_name == 'deepseek':
        response = deepseek_call('test', '', encryption_key, test_config=test_config) # Test call to check validity
        if isinstance(response, tuple): # If error returned
            update_llm_usability(llm_name, False) # Update usability status to False
            return response # Return error code and message
        
        update_llm_usability(llm_name, True) # Update usability status to True
        return 0 # Return successful response
    
    elif llm_name == 'claude':
        response = claude_call('test', '', encryption_key, test_config=test_config) # Test call to check validity
        if isinstance(response, tuple): # If error returned
            update_llm_usability(llm_name, False) # Update usability status to False
            return response # Return error code and message
        
        update_llm_usability(llm_name, True) # Update usability status to True
        return 0 # Return successful response


# Main llm call function
def call_llm_api(user_request, encryption_key):
    active_llm = get_config('active_llm') # Get active llm from config
    
    # Parse and Handle prompt 
    # Get stored instructions and decrypt
    stored_instructions_encrypted = get_config('prompt_instructions')
    stored_instructions = decrypt_data(stored_instructions_encrypted, encryption_key)
    client_location = get_config('location') # Get client location from config
    
    # Create full user request with instructions
    llm_instructions = f'Location: {client_location}\n, Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n'

    if stored_instructions != '':
        llm_instructions += f', Instructions: {stored_instructions}\n'
        
    # Filter based on active llm
    if active_llm == 'gemini':
        llm_response = gemini_call(user_request, llm_instructions, encryption_key,)
    elif active_llm == 'mistral':
        llm_response = mistral_call(user_request, llm_instructions, encryption_key)
    elif active_llm == 'chatgpt':
        llm_response = chatgpt_call(user_request, llm_instructions, encryption_key)
    elif active_llm == 'deepseek':
        llm_response = deepseek_call(user_request, llm_instructions, encryption_key)
    elif active_llm == 'claude':
        llm_response = claude_call(user_request, llm_instructions, encryption_key)
    else:
        return ('No Active LLM Configured, please configure an active LLM in the settings page.')

    # If error returned
    if isinstance(llm_response, tuple): 
        return f'LLM Error: {llm_response[0]} : {llm_response[1]}' # Return error code and message
    
    # Return successful response
    return llm_response


# Update active llm in config
def update_active_llm(llm_name):
    return update_config('active_llm', llm_name) 


# Update prompt instructions in config
def update_instructions(new_instructions, encryption_key):
    encrypted_instructions = encrypt_data(new_instructions, encryption_key) # Encrypt new instructions

    return update_config('prompt_instructions', encrypted_instructions) # Save updated config and return the full config


# Update llm usability status in config
def update_llm_usability(llm_name, usable_status):
    llm_configs = get_config('llm_configs') # Load current LLM configurations
    
    llm_configs[f'{llm_name}_config']['usable'] = usable_status # Update usability status
    update_config('llm_configs', llm_configs) # Save updated configurations
    

def update_llm_values(llm_name, new_api_key, new_model, encryption_key):
    # Cleanup inputs
    new_api_key = str(new_api_key).strip() # Clean API key input
    new_model = str(new_model).strip() # Clean model input
    
    # Load current configuration
    stored_llm_configs = get_config('llm_configs')
    
    # Encrypt and store the new configuration
    targets_config = stored_llm_configs[f'{llm_name}_config'] # Get existing target LLM config
    encrypted_api_key = encrypt_data(new_api_key, encryption_key) # Encrypt API key before storing
    
    # Update with new values
    targets_config['api_key'] = encrypted_api_key
    targets_config['model'] = new_model 
    
    # Save updated config back to parent config    
    stored_llm_configs[f'{llm_name}_config'] = targets_config # Save changes back to llm_configs
    update_config('llm_configs', stored_llm_configs) # Save updated llm_configs back to main config


# Gemini llm call
def gemini_call(prompt, llm_instructions, encryption_key, test_config=None):
    from google import genai
    from google.genai import types
    
    
    try: # Attempt to generate content
        # Define prefered model variable for assining for either testing or using stored config
        preferred_model = ''
        
        # If test api and model provided, use those (for testing validity)'
        if test_config:
            client = genai.Client(api_key=test_config[0]) # Initialize Gemini client with test API
            preferred_model = test_config[1]
            
        # Else use stored config
        else:
            gemini_config = get_config('llm_configs')['gemini_config'] # Load Gemini configuration
            client = genai.Client(api_key=decrypt_data(gemini_config['api_key'], encryption_key)) # Initialize Gemini client with decrypted API key
            preferred_model = gemini_config['model']
            


        response = client.models.generate_content(
            model=preferred_model, # Specify model from configuration
            contents=prompt, # Provide the prompt
            config=types.GenerateContentConfig(
                    system_instruction=llm_instructions,
                    # Turn on grounding with Google Search
                    tools=[
                        types.Tool(google_search=types.GoogleSearch())]
                    )
                )
        return response.text
    
    except Exception as e: # If failes
        try:
            return (e.status_code, e.body) # Return error message (error code, error message)
        except:
            return ('Failed', e.args[0]) # Otherwise return generic error


# Mistral llm call
def mistral_call(prompt, llm_instructions, encryption_key, test_config=None):
    from mistralai import Mistral
    
    # Define prefered model variable for assining for either testing or using stored config  
    prefered_model = ''
    
    try: # Attempt to generate content
        # If test api and model provided, use those (for testing validity)'
        if test_config:
            client = Mistral(api_key=test_config[0]) # Initialize Mistral client with test API
            prefered_model = test_config[1]
            
        # Else use stored config
        else:
            mistral_config = get_config('llm_configs')['mistral_config'] # Load Mistral configuration
            client = Mistral(api_key=decrypt_data(mistral_config['api_key'], encryption_key))
            prefered_model = mistral_config['model']
        
        
        response = client.chat.complete(
            model=prefered_model,
            messages=[
                {"role": "system", "content": llm_instructions},
                {"role": "user", "content": prompt},
                ],
            )
        return response.choices[0].message.content
    
    except Exception as e: # If failes
        try:
            return (e.status_code, e.body) # Return error message (error code, error message)
        except:
            return ('Failed', e.args[0]) # Otherwise return generic error


# Chatgpt llm call
# TODO: THIS NEEDS TO BE TESTED, ACCOUNT ISSUE WITH OPENAI SO TESTING ISNT POSSIBLE RIGHT NOW
def chatgpt_call(prompt, llm_instructions, encryption_key, test_config=None):
    from openai import OpenAI
    
    try: # Attempt to generate content
        # Define prefered model variable for assining for either testing or using stored config  
        prefered_model = ''
        
        # If test api and model provided, use those (for testing validity)'
        if test_config:
            client = OpenAI(api_key=test_config[0]) # Initialize ChatGPT client with test API
            chatgpt_config = {'model': test_config[1]}
        # Else use stored config
        else:
            chatgpt_config = get_config('llm_configs')['chatgpt_config'] # Load ChatGPT configuration
            client = OpenAI(api_key=decrypt_data(chatgpt_config['api_key'], encryption_key))
            prefered_model = chatgpt_config['model']

        
        response = client.responses.create(
            model=prefered_model,
            instructions=llm_instructions,
            input=prompt
        )
        return response.output_text
    except Exception as e: # If failes
        try:
            return (e.status_code, e.body) # Return error message (error code, error message)
        except:
            return ('Failed', e.args[0]) # Otherwise return generic error

# Deepseek llm call
def deepseek_call(prompt, llm_instructions, encryption_key, test_config=None):
    from openai import OpenAI
    
    try: # Attempt to generate content
        # Define prefered model variable for assining for either testing or using stored config  
        prefered_model = ''
        
        # If test api and model provided, use those (for testing validity)'
        if test_config:
            client = OpenAI(api_key=test_config[0], base_url="https://api.deepseek.com") # Initialize Deepseek client with test API
            prefered_model = test_config[1]
            
        # Else use stored config
        else:
            deepseek_config = get_config('llm_configs')['deepseek_config'] # Load Deepseek configuration
            client = OpenAI(api_key=decrypt_data(deepseek_config['api_key'], encryption_key), base_url="https://api.deepseek.com")
            prefered_model = deepseek_config['model']
            
            
        response = client.chat.completions.create(
            model=prefered_model,
            messages=[
                {"role": "system", "content": llm_instructions},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        a = response.choices[0].message.content
        return a
    except Exception as e: # If failes
        try:
            return (e.status_code, e.body) # Return error message (error code, error message)
        except:
            return ('Failed', e.args[0]) # Otherwise return generic error

# Claude llm call
def claude_call(prompt, llm_instructions, encryption_key, test_config=None):
    import anthropic
    
    try: # Attempt to generate content
        # Define prefered model variable for assining for either testing or using stored config  
        prefered_model = ''
        
        # If test api and model provided, use those (for testing validity)'
        if test_config:
            client = anthropic.Anthropic(api_key=test_config[0]) # Initialize Claude client with test API
            prefered_model = test_config[1]
            
        # Else use stored config
        else:
            claude_config = get_config('llm_configs')['claude_config'] # Load Claude configuration
            client = anthropic.Anthropic(api_key=decrypt_data(claude_config['api_key'], encryption_key))
            prefered_model = claude_config['model']


        response = client.messages.create(
            model=prefered_model,
            max_tokens=1000,
            system=llm_instructions,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            # TODO: add way to reliably parse tools in the future
            #,tools=[{"type": "web_search_20250305","name": "web_search","max_uses": 5}]
        )    
        return response.content[0].text
    except Exception as e: # If failes
        try:
            return (e.status_code, e.body) # Return error message (error code, error message)
        except:
            return ('Failed', e.args[0]) # Otherwise return generic error
