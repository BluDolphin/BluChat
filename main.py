import serial, time, datetime

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
    while True:
        response = send_command(modem, 'at+cmgl="REC UNREAD"')  # List all messages
        
        # if response contains new messages, save them to a file
        if "+CMGL:" in response: # +CMGL: is always in the beginning of a new message
            print("New SMS received")
            
            messages = parse_response(response) # Send response to parser function
            
            for message in messages:
                handle_message(message)
                
        time.sleep(2)


# Function to parse modem response for SMS messages
def parse_response(response):
    response_lines = response.splitlines()
    
    # data is stored nested as [list of message IDs, Sender, UnixTime, ResponseContent]
    messages = []  # Initialize with a dummy entry to handle multi-part messages
    
    for i in range(len(response_lines)):
        if response_lines[i].startswith('+CMGL:'):
            print('Found message header:', response_lines[i])
            
            # Data cleaning
            message_list = response_lines[i].split(',') # split by comma
            
            # delete index 1 and 3 (3 is 2 cause after first deletion the index shifts)
            # delete read unread line and empty string
            del message_list[1], message_list[2]
            
            
            # remove quotation marks from begignning and end of each element
            for j in range(len(message_list)):
                message_list[j] = message_list[j].strip('"')
                
            # Remove +CMGL: from the beginning of the first element
            message_list[0] = message_list[0].strip('+CMGL: ') 
            
            # Change message_list[0] to a list containing the message ID only
            message_list[0] = [int(message_list[0])]
            
            # convert date and time to unix timestamp 
            combined_date_time = message_list[2] + ',' + message_list[3].split('+')[0] # remove characted from after + in time segment
            full_date_time = datetime.datetime.strptime(combined_date_time, '%y/%m/%d,%H:%M:%S')
            unixtimestamp = full_date_time.timestamp()
            
            del message_list[2], message_list[2] # remove old date and time
            message_list.append(int(unixtimestamp)) # append new timestamp
            
            
            # append the actual message content (next line)
            message_list.append(response_lines[i+1])
            
            print('Cleaned message data:', message_list)
            
            
            # Dealing with multi SMS messages
            if len(messages) > 1:
                for message in messages:
                    # If timestamp is within 5 seconds and matching sender
                    if message[1] == message_list[1] and int(message[2]) <= int(message_list[2]) <= int(message[2]) + 5:  
                            print('Multi message found, appending content.')
                            message[3] += message_list[3]  # Append content
                            message[0].append(message_list[0][0])  # Append message ID
            
            messages.append(message_list)

    return messages


# Function to handle received messages
# Will be used later to trigger AI response or number filtering
def handle_message(message):
    sender = message[1]
    content = message[3]
    print(f"Message from {sender}: {content}")
    
    run_code = send_sms(sender, f"Auto-reply: Received your message '{content}'")
    
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
    time.sleep(2) # Wait for the modem to initialize
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
        time.sleep(3)
        
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
    time.sleep(2) # Wait for the modem to initialize
    modem.reset_input_buffer() # Clear any existing input   
    
    send_command(modem, "AT")      # Basic check
    send_command(modem, "ATE0")    # Turn off command echo
    send_command(modem, "AT+CMGF=1")  # Set SMS to text mode
    
    send_command(modem, "AT+CMGD=1,4")  # Delete all messages (clearing buffer)
    
    # start receiving SMS in background
    recieve_sms() 