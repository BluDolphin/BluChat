import serial, time, datetime, logging
from textwrap import wrap

from functions.phonenumber_functions import load_numbers
from functions.config_functions import get_config
from functions.sms_functions import call_llm_api

SERIAL_PORT = get_config('modem_interface')  # Adjust if your modem appears on a different port
BAUD_RATE = 115200

# define serial port as modem
MODEM = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=5)
MODEM.close()  # Ensure modem is closed initially

RUNNING_FLAG = False  # Flag to control service state (startup and shutdown)

logging.basicConfig(level=logging.INFO)

# Shared log class to allow multiple logs to receive messages
class SharedHomeLog:
    def __init__(self):
        self._loggers = [] # List of loggers to send messages to

    def add(self, logger):
        self._loggers.append(logger) # Add logger to list

    def remove(self, logger):
        if logger in self._loggers:
            self._loggers.remove(logger) # Remove logger from list

    def push(self, message):
        for logger in self._loggers:
            logger.push(message) # Push message to all loggers

CONSOLE_LOG = SharedHomeLog()


# Function to send AT commands and read responses
def send_command(command, delay=1):
    MODEM.write((command + '\r').encode())
    time.sleep(delay)
    response = MODEM.read_all().decode(errors='ignore')
    CONSOLE_LOG.push(f"> {command}\n{response}")
    return response


# Main function to receive SMS
def recieve_sms(key):    
    messages = []  # Initialize empty list to store messages
    
    while RUNNING_FLAG:               
        response = send_command('at+cmgl="REC UNREAD"')  # read all unread messages
        
        if "+CMGL:" in response: # +CMTI: is used as a notification for new messages
            CONSOLE_LOG.push("New SMS received")

            messages = parse_response(response, messages) # Send response to parser function
            
        # For each parsed message, handle it
        sent_messages = [] # List to store messages that have been handled
        for individual_message in messages: # For each message thats currently stored
            if individual_message[4] == True:  # If message has not had new messages
                handle_message(individual_message, key) # Handle the message
                sent_messages.append(individual_message) # Add to sent messages list to be removed later
            else:     
                individual_message[4] = True  # Mark message as having been handled as next loop will check for new messages again  
        
        
        # Delete message off modem and remove handled messages from main list
        for sent_msg in sent_messages: # For each message that has been handled
            CONSOLE_LOG.push(f"Deleting messages with IDs: {sent_msg[0]}")
            for msg_id in sent_msg[0]:
                send_command(f'AT+CMGD={msg_id}')
            messages.remove(sent_msg) # Remove from main messages list
            
        time.sleep(3)  # Check for new messages every 3 seconds


# Function to parse modem response for SMS messages
def parse_response(unread_response, current_parsed):
    
    # Split response into lines for processing
    unread_response = unread_response.splitlines()
    
    # Data is stored nested as [[list of message IDs], Sender, UnixTime, ResponseContent, No more responses]
    # Iterate through each line in the response
    for i in range(len(unread_response)):
        # Check for message header
        if unread_response[i].startswith('+CMGL:'):
            CONSOLE_LOG.push(f'Found message header: {unread_response[i]}') 
            
            # Split the header line into components
            active_response = unread_response[i].split(',') # split by comma
            
            # Delete index 1 and 3 (3 is 2 cause after first deletion the index shifts)
            # Delete read unread line and empty string
            del active_response[1], active_response[2]
            
            # Remove quotation marks from begignning and end of each element
            for j in range(len(active_response)):
                active_response[j] = active_response[j].strip('"')
                
            # Remove +CMGL: from the beginning of the first element
            active_response[0] = active_response[0].strip('+CMGL: ') 
            
            # Change active_response[0] to a list containing the message ID only
            active_response[0] = [int(active_response[0])]
            
            # convert date and time to unix timestamp 
            combined_date_time = active_response[2] + ',' + active_response[3].split('+')[0] # remove characted from after + in time segment
            full_date_time = datetime.datetime.strptime(combined_date_time, '%y/%m/%d,%H:%M:%S')
            unixtimestamp = full_date_time.timestamp()
            
            del active_response[2], active_response[2] # remove old date and time
            active_response.append(int(unixtimestamp)) # append new timestamp
            
            
            # append the actual message content (next line)
            active_response.append(unread_response[i+1])
            
            # Append False as placeholder for has been handled fully
            active_response.append(True) 
                        
            
            # If first message, just append
            if not current_parsed:
                active_response[4] = False  # Indicate message has been handled recently
                current_parsed.append(active_response)
                continue # Skip to next iteration (avoids multi SMS handling for first message)
                
            # Dealing with multi SMS messages
            for message in current_parsed: # For each stored message
                # If timestamp is within 5 seconds and matching sender
                if message[1] == active_response[1] and int(message[2])-10 <= int(active_response[2]) <= int(message[2])+10:  
                    CONSOLE_LOG.push('Multi message found, appending content.')
                    
                    message[2] = int(active_response[2])  # Update timestamp to latest message to deal with further multi SMS
                    message[3] += active_response[3]  # Append SMS content to existing message
                    message[4] = False  # Indicate message has been handled recently
                    message[0].append(active_response[0][0])  # Append SMS ID to list of IDs
                    break
                else:
                    # If no match found, append as new message
                    active_response[4] = False  # Indicate message has been handled recently
                    current_parsed.append(active_response)
                    break
                
    CONSOLE_LOG.push(current_parsed)        
    return current_parsed


# Function to handle received messages
# Will be used later to trigger AI response or number filtering
def handle_message(message, key):
    sender = message[1]
    content = message[3]
    CONSOLE_LOG.push(f"Message from {sender}: {content}")
    
    # Check whitelist setting
    whitelist_toggle = get_config('whitelist_toggle')
    if whitelist_toggle: # If whitelist is enabled
        CONSOLE_LOG.push("Whitelist is enabled.")    
        if not check_authentication(sender, key, whitelist_toggle): # If sender is not authorized
            CONSOLE_LOG.push("Unauthorized sender. Ignoring message.")
            send_sms(sender, "Your number is not authorized to use this service.")#
            return
        CONSOLE_LOG.push("Authorized sender. Processing message...")
    else: # Whitelist is disabled
        CONSOLE_LOG.push("Whitelist is disabled.")

    # Call LLM to generate response
    llm_response = call_llm_api(content, key)
    
    # Auto-reply with segmented message
    segmented_message = wrap(llm_response, 150)  # Split content into 150 character chunks
    send_sms('07591432022', f"Auto-reply: Received your message, processing...")
        
    for indivitual_segment in segmented_message:
        run_code = send_sms(sender, indivitual_segment)
        
        if run_code == 0:
            CONSOLE_LOG.push("✅ SMS sent successfully!")
        elif run_code == 1:
            CONSOLE_LOG.push("❌ SMS sending failed.")
        else:
            CONSOLE_LOG.push(f"❌ An error occurred: {run_code}")


# Function to check if sender is authorised
def check_authentication(sender, key, toggle):
    if toggle == False:
        return True
    
    authorized_numbers = load_numbers(key)
    country_code = get_config('country_code')
        
    for entry in authorized_numbers:
        # Convert local UK number to international format
        if not entry['number'].startswith('+'):
            entry['number'] = entry['number'][1:] # Cut first number 
            entry['number'] = country_code + entry['number']  # Convert to international format
        
        if entry['number'] == sender and entry['active']:
            return True
            
    return False

    
# Main function to send SMS
def send_sms(phone, message):
    MODEM.reset_input_buffer() # Clear any existing input
    
    try:
        response = send_command(f'AT+CMGS="{phone}"')
    
        # Check if > was in response as its needed to send messages
        # If no then a problem occurred
        if ">" not in response:
            CONSOLE_LOG.push("❌ Did not receive SMS prompt. Aborting.")
            return

        # Ctrl+Z ends the message
        MODEM.write(message.encode() + b"\x1A")  
        time.sleep(2)
        
        # Get modem response
        response = MODEM.read_all().decode(errors='ignore') 
        CONSOLE_LOG.push(f"SMS send response:\n{response}")

        if "OK" in response:
            return 0
        else:
            return 1
    except Exception as e:
        return e


# start and stop service functions
def start_sms_service(key):   
    # Define flag as global
    global RUNNING_FLAG
    
    # Prevent multiple instances
    if RUNNING_FLAG == True:
        return
    
    RUNNING_FLAG = True
    MODEM.open()  # Open modem connection

    # Check modem connection
    if "OK" not in send_command("AT"):
        CONSOLE_LOG.push("❌ Modem not responding. Check connection.")
        CONSOLE_LOG.push("Aborted start.")
        RUNNING_FLAG = False
        return
    
    # Setup modem
    CONSOLE_LOG.push("Starting SMS service...")
    send_command("ATE0")    # Turn off command echo
    send_command("AT+CMGF=1")  # Set SMS to text mode
    send_command("AT+CMGD=1,4")  # Delete all messages (clearing buffer)
    
    # Start receiving SMS in background
    recieve_sms(key)
    
    # Close modem connection after stopped
    MODEM.close()
    CONSOLE_LOG.push("Modem connection closed.")

def stop_sms_service():
    global RUNNING_FLAG # Define flag as global
    
    # if service is already stopped, do nothing
    if RUNNING_FLAG == False:
        return
    
    RUNNING_FLAG = False
    # Stopping message
    CONSOLE_LOG.push("Stopping SMS service...")
        