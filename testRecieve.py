import serial, time, logging

logging.basicConfig(level=logging.DEBUG)

serial_port = "/dev/ttyAMA0"  # Adjust if your modem appears on a different port
baud_rate = 115200
phone_number = ""  # Replace with your target number
message = ""

# Function to send AT commands and read responses
def send_command(modem, command, delay=1):
    modem.write((command + '\r').encode())
    time.sleep(delay)
    response = modem.read_all().decode(errors='ignore')
    logging.debug(f"> {command}\n{response}")
    return response
    
# Main function to receive SMS
def recieve_sms(phone, message):
    with serial.Serial(serial_port, baud_rate, timeout=5) as modem: # Open serial port
        time.sleep(2) # Wait for the modem to initialize
        modem.reset_input_buffer() # Clear any existing input   
        
        send_command(modem, "AT")      # Basic check
        send_command(modem, "ATE0")    # Turn off command echo
        
        while True:
            response = send_command(modem, 'at+cmgl="REC UNREAD"')  # List all messages
            
            # if response contains new messages, save them to a file
            if "+CMGL:" in response: # +CMGL: is always in the beginning of a new message
                logging.debug("new Message Received!")
                with open("received_messages.txt", "w") as f:
                    f.write(response + "\n")
                    
            response = ""  # Clear response to avoid infinite loop
                    
            time.sleep(2)

if __name__ == "__main__":
    recieve_sms(phone_number, message)