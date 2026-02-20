import serial, time, datetime, logging, threading
from textwrap import wrap

from functions.group_functions import load_group_config
from functions.phonenumber_functions import check_sender_auth, check_number_exists
from functions.config_functions import get_config
from functions.llm_functions import call_llm_api


SERIAL_PORT = get_config('modem_interface')  # Adjust if your modem appears on a different port
BAUD_RATE = 115200

# Do not open serial port at import time; create on-demand in start/stop
MODEM = None

RUNNING_FLAG = False  # Flag to control service state (startup and shutdown)

sms_thread = None

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
    try:
        MODEM.write((command + '\r').encode())
        time.sleep(delay)
        response = MODEM.read_all().decode(errors='ignore')
        CONSOLE_LOG.push(f"> {command}\n{response}")
        return response
    except Exception as e:
        CONSOLE_LOG.push(f'ERROR: Exception in send_command: {e}')
        return ''


# Main function to receive SMS
def recieve_sms(key):      
    messages = []  # Initialize empty list to store messages
    
    while RUNNING_FLAG:               
        response = send_command('at+cmgl="REC UNREAD"')  # read all unread messages
        
        if "+CMGL:" in response: # +CMTI: is used as a notification for new messages
            CONSOLE_LOG.push("INFO: New SMS received")

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
            CONSOLE_LOG.push(f'DEBUG: Found message header: {unread_response[i]}') 
            
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
                    CONSOLE_LOG.push('DEBUG: Multi message found, appending content.')
                    
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
    CONSOLE_LOG.push(f"INFO: Message from {sender}: {content}")
    
    # Acknowledge message receipt
    send_sms(sender, f'Auto-reply: Received your message, processing...')
    
    # === Whitelist Check ===
    # Get global whitelist setting
    whitelist_toggle = get_config('global_whitelist')
    number_config = check_sender_auth(sender, whitelist_toggle, key)

    if whitelist_toggle: # If whitelist is enabled
        CONSOLE_LOG.push('INFO: Whitelist is enabled.')   
         
        # If number not found in stored numbers or number is marked as blocked
        if number_config == False or (isinstance(number_config, tuple) and number_config[0] == True):
            # Send rejection message
            CONSOLE_LOG.push('INFO: Unauthorized sender. Ignoring message.')
            send_sms(sender, 'Your number is not authorized to use this service.') 
            return # Exit function without processing further
        
        CONSOLE_LOG.push('INFO: Authorized sender. Processing message...')
    else: # Whitelist is disabled
        CONSOLE_LOG.push('INFO: Whitelist is disabled.')

    # === Group Check ===
    # If number has group assigned
    if (isinstance(number_config, tuple) and number_config[1] != 'None'):
        CONSOLE_LOG.push(f'DEBUG: Number assigned to group: {number_config[1]}')
        # load group info and prep
        group_config = load_group_config(number_config[1], key) # Load group config - returns (blocked, model, instructions)

        if group_config[0] == True: # If group is blocked
            CONSOLE_LOG.push('INFO: Group is blocked. Ignoring message.')
            send_sms(sender, 'Your group is currently blocked from using this service.') 
            return # Exit function without processing further
                
    else: # Else no group assigned
        CONSOLE_LOG.push('INFO: No group assigned to number.')
        group_config = None
        
    # === Generate response ===
    # If group config doesn't exist will pass None
    llm_response = call_llm_api(content, key, group_config)
    CONSOLE_LOG.push(f'INFO: LLM response:\n{llm_response}')
    
    # Reply with segmented LLM message
    segmented_message = wrap(llm_response, 150)  # Split content into 150 character chunks
        
    for indivitual_segment in segmented_message:
        run_code = send_sms(sender, indivitual_segment)
        
        if run_code == 0:
            CONSOLE_LOG.push('INFO: ✅ SMS sent successfully!')
        elif run_code == 1:
            CONSOLE_LOG.push('INFO: ❌ SMS sending failed.')
        else:
            CONSOLE_LOG.push(f'INFO: ❌ An error occurred: {run_code}')
    
# Main function to send SMS
def send_sms(phone, message):
    MODEM.reset_input_buffer() # Clear any existing input
    
    try:
        response = send_command(f'AT+CMGS="{phone}"')
    
        # Check if > was in response as its needed to send messages
        # If no then a problem occurred
        if '>' not in response:
            CONSOLE_LOG.push('INFO: ❌ Did not receive SMS prompt. Aborting.')
            return 1

        # Ctrl+Z ends the message
        MODEM.write(message.encode() + b'\x1A')  
        time.sleep(2)
        
        # Get modem response
        response = MODEM.read_all().decode(errors='ignore') 
        CONSOLE_LOG.push(f'INFO: SMS send response:\n{response}')

        if 'OK' in response:
            return 0
        else:
            return 1
    except Exception as e:
        return e


# start and stop service functions
def start_sms_service(key):   
    # Define flag as global
    global RUNNING_FLAG
    global MODEM
    global sms_thread
    
    # Prevent multiple instances
    if RUNNING_FLAG == True:
        return
    
    RUNNING_FLAG = True
    
    # Try to open modem connection
    # Attempt range 0-1 (2 attempts)
    for attempt in range(2):
        try:
            if attempt == 1: # Try again by closing and reopening connection
                CONSOLE_LOG.push('INFO: Attempting to close and re-open...')
                if MODEM:
                    try:
                        MODEM.close()
                    except Exception:
                        pass
                time.sleep(2)
                
            # Open serial port and assign to global variable
            if MODEM is None:
                MODEM = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=5)
            else:
                try:
                    MODEM.open()
                    break  # If open successful, break out of loop
                except Exception:
                    pass
            
            # Test connection
            modem_test = send_command('AT')
            if 'OK' in modem_test: # If connection successful
                break  # Exit retry loop and continue startup
            
            # If no OK received, raise error to trigger exception handling
            CONSOLE_LOG.push('ERROR: ❌ Modem not responding. Retrying...')
            raise ConnectionError(modem_test)
            
        except Exception as e:
            CONSOLE_LOG.push(f'ERROR: ❌ Could not open modem connection: {e}')
            
            if attempt == 1:  # Final attempt failed
                CONSOLE_LOG.push('ERROR: Aborted start.')
                RUNNING_FLAG = False
                return

    # Setup modem
    CONSOLE_LOG.push('INFO: Starting SMS service...')
    send_command('ATE0')    # Turn off command echo
    send_command('AT+CMGF=1')  # Set SMS to text mode
    send_command('AT+CMGD=1,4')  # Delete all messages (clearing buffer)
    
    # Start receiving SMS in background thread so main program is not blocked
    sms_thread = threading.Thread(target=recieve_sms, args=(key,), daemon=True)
    sms_thread.start()

    # Note: MODEM will be closed by stop_sms_service()
    CONSOLE_LOG.push('INFO: Modem receive thread started.')
    
    # Return from function
    return 


def stop_sms_service():
    global RUNNING_FLAG # Define flag as global
    global MODEM
    # Stopping message
    CONSOLE_LOG.push('INFO: Stopping SMS service...')
    
    # if service is already stopped, do nothing
    if RUNNING_FLAG == False:
        return
    
    RUNNING_FLAG = False
    
    # Wait for sms_thread to finish
    sms_thread.join(timeout=30)  # Wait up to 30 seconds for thread to finish
    
    # close modem if open
    try:
        if MODEM:
            MODEM.close()
            CONSOLE_LOG.push('INFO: Modem connection closed.')
    except Exception as e:
        CONSOLE_LOG.push(f'ERROR: Exception while closing modem: {e}')
    
    # Return from function
    return