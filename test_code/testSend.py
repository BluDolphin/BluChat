import serial, time, logging

logging.basicConfig(level=logging.DEBUG)

SERIAL_PORT = "/dev/ttyAMA0"  # Adjust if your modem appears on a different port
BAUD_RATE = 115200
PHONE_NUMBER = "+[PhoneNumber]"  # Replace with your target number
MESSAGE = "Python test"

# Function to send AT commands and read responses
def send_command(modem, command, delay=1):
    modem.write((command + '\r').encode())
    time.sleep(delay)
    response = modem.read_all().decode(errors='ignore')
    logging.debug(f"> {command}\n{response}")
    return response

# Main function to send SMS
def send_sms(phone, message):
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=5) as modem: # Open serial port
        time.sleep(2) # Wait for the modem to initialize
        modem.reset_input_buffer() # Clear any existing input

        send_command(modem, "AT")      # Basic check
        send_command(modem, "ATE0")    # Turn off command echo
        resp = send_command(modem, "AT+CMGF=1")  # Set SMS to text mode
        
        if "ERROR" in resp:
            print("❌ Could not set SMS text mode. Aborting.")
            return

        resp = send_command(modem, f'AT+CMGS="{phone}"')
        if ">" not in resp:
            print("❌ Did not receive SMS prompt. Aborting.")
            return

        # Ctrl+Z ends the message
        modem.write(message.encode() + b"\x1A")  
        time.sleep(5)
        
        # Get modem response
        response = modem.read_all().decode(errors='ignore') 
        print("SMS send response:\n", response)

        if "OK" in response:
            print("✅ SMS sent successfully!")
        else:
            print("❌ SMS may have failed.")

if __name__ == "__main__":
    send_sms(PHONE_NUMBER, MESSAGE)