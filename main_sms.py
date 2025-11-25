import serial, time, datetime, logging
import hmac, hashlib
from textwrap import wrap

SERIAL_PORT = "/dev/ttyAMA0"  # Adjust if your modem appears on a different port
BAUD_RATE = 115200

# define serial port as modem
MODEM = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=5)
running_flag = False

logging.basicConfig(level=logging.INFO)


# Function to send AT commands and read responses
def send_command(command, delay=1):
    MODEM.write((command + '\r').encode())
    time.sleep(delay)
    response = MODEM.read_all().decode(errors='ignore')
    console_log.push(f"> {command}\n{response}")
    return response


# Main function to receive SMS
def recieve_sms(hash_key):    
    messages = []  # Initialize empty list to store messages
    
    while running_flag:               
        response = send_command('at+cmgl="REC UNREAD"')  # read all unread messages
        
        if "+CMGL:" in response: # +CMTI: is used as a notification for new messages
            console_log.push("New SMS received")

            messages = parse_response(response, messages) # Send response to parser function
            
        # For each parsed message, handle it
        sent_messages = [] # List to store messages that have been handled
        for individual_message in messages: # For each message thats currently stored
            if individual_message[4] == True:  # If message has not had new messages
                handle_message(individual_message, hash_key) # Handle the message
                sent_messages.append(individual_message) # Add to sent messages list to be removed later
            else:     
                individual_message[4] = True  # Mark message as having been handled as next loop will check for new messages again  
        
        
        # Delete message off modem and remove handled messages from main list
        for sent_msg in sent_messages: # For each message that has been handled
            console_log.push(f"Deleting messages with IDs: {sent_msg[0]}")
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
            console_log.push('Found message header:', unread_response[i]) 
            
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
            
            #console_log.push('Cleaned message data: ', active_response)
            
            
            # If first message, just append
            if not current_parsed:
                active_response[4] = False  # Indicate message has been handled recently
                current_parsed.append(active_response)
                continue # Skip to next iteration (avoids multi SMS handling for first message)
                
            # Dealing with multi SMS messages
            for message in current_parsed: # For each stored message
                # If timestamp is within 5 seconds and matching sender
                if message[1] == active_response[1] and int(message[2])-10 <= int(active_response[2]) <= int(message[2])+10:  
                    console_log.push('Multi message found, appending content.')
                    
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
                
    console_log.push(current_parsed)        
    return current_parsed


# Function to handle received messages
# Will be used later to trigger AI response or number filtering
def handle_message(message, hash_key):
    sender = message[1]
    content = message[3]
    console_log.push(f"Message from {sender}: {content}")
    
    if not check_authentication(sender, hash_key):
        console_log.push("Unauthorized sender. Ignoring message.")
        send_sms(sender, "Your number is not authorized to use this service.")#
        
    else:
        segmented_message = wrap(content, 150)  # Split content into 150 character chunks
        send_sms(sender, f"Auto-reply: Received your message, processing...")
        
        for indivitual_segment in segmented_message:
            run_code = send_sms(sender, indivitual_segment)
            
            if run_code == 0:
                console_log.push("✅ SMS sent successfully!")
            elif run_code == 1:
                console_log.push("❌ SMS sending failed.")
            else:
                console_log.push(f"❌ An error occurred: {run_code}")
        

def check_authentication(sender, hash_key):
    with open("data/authorised_numbers.txt", "r") as f:
        authorized_numbers = f.read().splitlines()
    
    hash_key = hash_key.encode('utf-8')
    sender_hashed = hmac.new(hash_key, sender.encode('utf-8'), hashlib.sha512).digest()
    
    if sender_hashed.hex() in authorized_numbers:
        return True

    
# Main function to send SMS
def send_sms(phone, message):
    MODEM.reset_input_buffer() # Clear any existing input
    
    try:
        response = send_command(f'AT+CMGS="{phone}"')
    
        # Check if > was in response as its needed to send messages
        # If no then a problem occurred
        if ">" not in response:
            console_log.push("❌ Did not receive SMS prompt. Aborting.")
            return

        # Ctrl+Z ends the message
        MODEM.write(message.encode() + b"\x1A")  
        time.sleep(2)
        
        # Get modem response
        response = MODEM.read_all().decode(errors='ignore') 
        console_log.push("SMS send response:\n", response)

        if "OK" in response:
            return 0
        else:
            return 1
    except Exception as e:
        return e


# start and stop service functions
def start_service(hash_key, home_log):   
    # Define flag as global
    global running_flag
    global console_log
    
    # Prevent multiple instances
    if running_flag == True:
        return
    
    running_flag = True
    console_log = home_log
    
    # Check modem connection
    if "OK" not in send_command("AT"):
        console_log.push("❌ Modem not responding. Check connection.")
        console_log.push("Aborted start.")
        running_flag = False
        return
    
    # Setup modem
    console_log.push("Starting SMS service...")
    send_command("ATE0")    # Turn off command echo
    send_command("AT+CMGF=1", 3)  # Set SMS to text mode
    send_command("AT+CMGD=1,4")  # Delete all messages (clearing buffer)
    
    # Start receiving SMS in background
    recieve_sms(hash_key)
    
    # Close modem connection after stopped
    MODEM.close()
    console_log.push("Modem connection closed.")

def stop_service():
    global running_flag # Define flag as global
    
    # if service is already stopped, do nothing
    if running_flag == False:
        return
    
    running_flag = False
    # Stopping message
    console_log.push("Stopping SMS service...")
        