import serial, time, datetime
from textwrap import wrap

serial_port = "/dev/ttyAMA0"  # Adjust if your modem appears on a different port
baud_rate = 115200

# define serial port as modem
modem = serial.Serial(serial_port, baud_rate, timeout=5)

# Function to send AT commands and read responses
def send_command(modem, command, delay=1):
    modem.write((command + '\r').encode())
    time.sleep(delay)
    response = modem.read_all().decode(errors='ignore')
    print(f"> {command}\n{response}")
    return response


# Main function to receive SMS
def recieve_sms():    
    messages = []  # Initialize empty list to store messages
    
    while True:        
        response = send_command(modem, 'at+cmgl="REC UNREAD"')  # List all messages
        
        # if response contains new messages, save them to a file
        if "+CMGL:" in response: # +CMGL: is always in the beginning of a new message
            print("New SMS received")
            
            messages = parse_response(response, messages) # Send response to parser function
            
        # For each parsed message, handle it
        sent_messages = [] # List to store messages that have been handled
        for individual_message in messages: # For each message thats currently stored
            if individual_message[4] == True:  # If message has not had new messages
                handle_message(individual_message) # Handle the message
                sent_messages.append(individual_message) # Add to sent messages list to be removed later
            else:     
                individual_message[4] = True  # Mark message as having been handled as next loop will check for new messages again  
        
        # Remove handled messages from the main list
        for sent_msg in sent_messages: # For each message that has been handled
            messages.remove(sent_msg) # Remove from main messages list
            
        time.sleep(3)  # Check for new messages every 5 seconds

# Function to parse modem response for SMS messages
def parse_response(unread_response, current_parsed):
    
    # Split response into lines for processing
    unread_response = unread_response.splitlines()
    
    # Data is stored nested as [[list of message IDs], Sender, UnixTime, ResponseContent, No more responses]
    
    # Iterate through each line in the response
    for i in range(len(unread_response)):
        # Check for message header
        if unread_response[i].startswith('+CMGL:'):
            print('Found message header:', unread_response[i]) 
            
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
            
            #print('Cleaned message data: ', active_response)
            
            
            # If first message, just append
            if not current_parsed:
                active_response[4] = False  # Indicate message has been handled recently
                current_parsed.append(active_response)
                continue # Skip to next iteration (avoids multi SMS handling for first message)
                
            # Dealing with multi SMS messages
            for message in current_parsed: # For each stored message
                # If timestamp is within 5 seconds and matching sender
                if message[1] == active_response[1] and int(message[2])-10 <= int(active_response[2]) <= int(message[2])+10:  
                    print('Multi message found, appending content.')
                    
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
 
                
    print(current_parsed)        
    return current_parsed

# Function to handle received messages
# Will be used later to trigger AI response or number filtering
def handle_message(message):
    sender = message[1]
    content = message[3]
    print(f"Message from {sender}: {content}")
    
    segmented_message = wrap(content, 150)  # Split content into 150 character chunks
    send_sms(sender, f"Auto-reply: Received your message, processing...")
    
    for indivitual_segment in segmented_message:
        run_code = send_sms(sender, indivitual_segment)
        
        if run_code == 0:
            print("✅ SMS sent successfully!")
        elif run_code == 1:
            print("❌ SMS sending failed.")
        else:
            print(f"❌ An error occurred: {run_code}")
        
        
    print(f"Deleting messages with IDs: {message[0]}")
    # Delete messages from modem
    for msg_id in message[0]:
        send_command(modem, f'AT+CMGD={msg_id}')


# Main function to send SMS
def send_sms(phone, message):
    modem.reset_input_buffer() # Clear any existing input
    try:
        response = send_command(modem, f'AT+CMGS="{phone}"')
    
        # Check if > was in response as its needed to send messages
        # If no then a problem occurred
        if ">" not in response:
            print("❌ Did not receive SMS prompt. Aborting.")
            return

        # Ctrl+Z ends the message
        modem.write(message.encode() + b"\x1A")  
        time.sleep(2)
        
        # Get modem response
        response = modem.read_all().decode(errors='ignore') 
        print("SMS send response:\n", response)

        if "OK" in response:
            return 0
        else:
            return 1
    except Exception as e:
        return e


if __name__ == "__main__":  
    # Setup modem
    time.sleep(3) # Wait for the modem to initialize
    modem.reset_input_buffer() # Clear any existing input   
    
    send_command(modem, "AT")      # Basic check
    send_command(modem, "ATE0")    # Turn off command echo
    send_command(modem, "AT+CMGF=1", 3)  # Set SMS to text mode
    
    send_command(modem, "AT+CMGD=1,4")  # Delete all messages (clearing buffer)
    
    # start receiving SMS in background
    recieve_sms() 