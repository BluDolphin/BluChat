import time, datetime, serial, asyncio
from textwrap import wrap

from functions.group_functions import load_group_config
from functions.phonenumber_functions import check_sender_config
from functions.config_functions import get_config
from functions.llm_functions import call_llm_api


SERIAL_PORT = None # Config is loades in start function
BAUD_RATE = 115200
MODEM = serial.Serial() # Create an unconfigured Serial instance - configs are set on run


RUNNING_FLAG = False  # Flag to control service state (startup and shutdown)

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
def send_command(command):
    MODEM.write((command + '\r').encode())
    time.sleep(1)
    response = MODEM.read_all().decode(errors='ignore')
    CONSOLE_LOG.push(f"> {command}\n{response}")
    return response


# Main function to receive SMS
def recieve_sms(messages):    
    response = send_command('at+cmgl="REC UNREAD"')  # read all unread messages
    
    if "+CMGL:" in response: # +CMTI: is used as a notification for new messages
        CONSOLE_LOG.push("INFO: New SMS received")

        messages = parse_response(response, messages) # Send response to parser function
         
    return messages


# Main function to send SMS
def send_sms(sender, segmented_message):
    MODEM.reset_input_buffer() # Clear any existing input
    
    #if message is just as string convert it to a list
    if isinstance(segmented_message, str):
        segmented_message = [segmented_message]
    
    
    for individual_segment in segmented_message:
        try:
            response = send_command(f'AT+CMGS="{sender}"') # Send Prep send command
        
            # Check if > was in response as its needed to send messages
            # If no then a problem occurred
            if '>' not in response:
                CONSOLE_LOG.push('INFO: ❌ Did not receive SMS prompt. Aborting.')

            # Ctrl+Z ends the message
            MODEM.write(individual_segment.encode() + b'\x1A') # Send message segment
            time.sleep(2)
            
            # Get modem response
            response = MODEM.read_all().decode(errors='ignore') 
            CONSOLE_LOG.push(f'INFO: SMS send response:\n{response}')

            if 'OK' in response:
                CONSOLE_LOG.push('INFO: ✅ SMS segment sent successfully!')
            else:
                CONSOLE_LOG.push('INFO: ❌ SMS sending failed.')
                
        except Exception as e:
            CONSOLE_LOG.push(f'INFO: ❌ An error occurred: {e}')


# Function to parse modem response for SMS messages
def parse_response(unread_response, current_parsed):
    
    # Split response into lines for processing
    unread_response = unread_response.splitlines()
    
    # Data is stored nested as [[list of message IDs], Sender, UnixTime, ResponseContent, No more responses]
    # Iterate through each line in the response
    for i in range(len(unread_response)):
        # Check for message header
        if unread_response[i].startswith('+CMGL:'):
            #CONSOLE_LOG.push(f'DEBUG: Found message header: {unread_response[i]}') 
            
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
            
            # Placeholder for if message is/has been handled (prevent duplicate asyncs)
            active_response.append(False)
                        
            
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
    
    CONSOLE_LOG.push(f'DEBUG: Current parsed messages: {current_parsed}')            
    #CONSOLE_LOG.push(current_parsed)        
    return current_parsed


# Function to handle received messages
# Will be used later to trigger AI response or number filtering
async def handle_message(message, key):
    sender = message[1]
    content = message[3]

    # === Whitelist Check ===
    # Get global whitelist setting
    whitelist_toggle = get_config('global_whitelist')
    number_config = check_sender_config(sender, whitelist_toggle, key)

    if whitelist_toggle: # If whitelist is enabled
        CONSOLE_LOG.push('DEBUG: Whitelist is enabled.')   
         
        # If number not found in stored numbers or number is marked as blocked
        if number_config[0] == True:
            # Send rejection message
            CONSOLE_LOG.push('DEBUG: Unauthorized sender. Ignoring message.')
            return 'Your number is not authorized to use this service.' # Exit function without processing further
        
        CONSOLE_LOG.push('DEBUG: Authorized sender. Processing message...')
    else: # Whitelist is disabled
        CONSOLE_LOG.push('DEBUG: Whitelist is disabled.')

    # === Group Check ===
    # If number has group assigned
    if number_config[1] != 'None':
        CONSOLE_LOG.push(f'DEBUG: Number assigned to group: {number_config[1]}')
        # load group info and prep
        group_config = load_group_config(number_config[1], key) # Load group config - returns (blocked, model, instructions)

        if group_config[0] == True: # If group is blocked
            CONSOLE_LOG.push('DEBUG: Group is blocked. Ignoring message.')
            return 'Your group is currently blocked from using this service.' # Exit function without processing further
        
    else: # Else no group assigned
        CONSOLE_LOG.push('DEBUG: No group assigned to number.')
        group_config = None
        
    # === Generate response ===
    # If group config doesn't exist will pass None
    llm_response = call_llm_api(content, key, group_config)
    
    # Reply with segmented LLM message
    segmented_message = wrap(llm_response, 150)  # Split content into 150 character chunks
    
    return segmented_message

            
async def main(key):
    messages = []  # Initialize empty list to store messages
    sent_messages = [] # List to keep track of sent messages for deletion after response
    async_tasks = [] # List to keep track of async tasks for handling messages
    
    while RUNNING_FLAG:
        messages = recieve_sms(messages) # Get new messages 

        # For each parsed message, handle it
        for individual_msg in messages: # For each message thats currently stored
            # Check if message has been handled recently (False means it hasnt)
            if individual_msg[4] == False: # if message has been recently parsed
                individual_msg[4] = True # Mark ready (can be reset if new message appended)
                continue # Dont parse, and go to next message
            # Check if message has/is being handled (True means it is/has been)
            if individual_msg[5] == True: # if message is/has been handled
                continue # Dont parse, and go to next message
            
            # Acknowledge message receipt
            send_sms(individual_msg[1], f'Auto-reply: Received your message, processing...')
            CONSOLE_LOG.push(f"INFO: Acknowledged message from {individual_msg[1]}.\n"
                             f"INFO: Handling message {individual_msg}")
            # Mark as processing 
            individual_msg[5] = True 
            task = asyncio.create_task(handle_message(individual_msg, key))
            
            # Callback function to run when task is done
            def on_finish(task, msg=individual_msg): 
                if task.exception(): # Check for exceptions in the task
                    CONSOLE_LOG.push(f'INFO: ❌ Error handling message from {msg[1]}: {task.exception()}') # response = task.result() # Get the result from the task (the segmented)
                    return
                # Send the response back to the sender
                send_sms(msg[1], task.result()) # Send the response back to the sender
                
                sent_messages.append(msg) # Add message to sent messages list for deletion
                                
            task.add_done_callback(on_finish) # Add callback to run when task is done
            async_tasks.append(task)
            
            
        # Delete processed messages from modem and memory
        for msg in sent_messages:
            CONSOLE_LOG.push(f"Deleting message with ID: {msg[0]}")
                
            for msg_id in msg[0]:
                send_command(f'AT+CMGD={msg_id}') # Clear from sim card
            
            messages.remove(msg) # Clear from stored messages list
            sent_messages.remove(msg) # Clear sent messages list for next loop    
 
        await asyncio.sleep(2)  # Check for new messages every 3 seconds (send_command had 1 seccond delay)


# start and stop service functions
def start_sms_service(key):   
    # Define flag as global
    global RUNNING_FLAG
    global SERIAL_PORT
    
    # Prevent multiple instances
    if RUNNING_FLAG == True:
        return
    
    RUNNING_FLAG = True
    SERIAL_PORT = get_config('modem_interface')  # Set modem interface from config
    
    # Try to open modem connection
    # Attempt range 0-1 (2 attempts)
    for attempt in range(2):
        try:
            # Pass modem configs to the Serial instance
            MODEM.port = SERIAL_PORT
            MODEM.baudrate = BAUD_RATE
            MODEM.timeout = 5

            if attempt == 1: # Try again by closing and reopening connection
                CONSOLE_LOG.push('INFO: Attempting to close and re-open...')
                MODEM.close()
                time.sleep(2)

            MODEM.open() 
            
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
    
    # Start receiving SMS in background
    asyncio.run(main(key))
    
    # Close modem connection after stopped
    MODEM.close()
    RUNNING_FLAG = False
    CONSOLE_LOG.push('INFO: Modem connection closed.')


def stop_sms_service():
    global RUNNING_FLAG # Define flag as global
    
    # if service is already stopped, do nothing
    if RUNNING_FLAG == False:
        CONSOLE_LOG.push('INFO: SMS service is not running.')
        return
    
    RUNNING_FLAG = False
    # Stopping message
    CONSOLE_LOG.push('INFO: Stopping SMS service...')