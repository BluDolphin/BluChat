with open('multiSMS.txt', 'r') as file:
    response = file.read()

import datetime

def parse_response(unread_response):
    
    # Split response into lines for processing
    unread_response = unread_response.splitlines()
    
    # Data is stored nested as [list of message IDs, Sender, UnixTime, ResponseContent]
    messages = []  # Initialize messages list of messages to be returned
    
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
            
            print('Cleaned message data: ', active_response)
            
            # If first message, just append
            if not messages:
                messages.append(active_response)
                continue # Skip to next iteration (avoids multi SMS handling for first message)
                
            # Dealing with multi SMS messages
            for stored_message in messages: # For each stored message
                # If timestamp is within 5 seconds and matching sender
                if stored_message[1] == active_response[1] and int(stored_message[2]) <= int(active_response[2]) <= int(stored_message[2]) + 5:  
                    print('Multi message found, appending content.')
                    
                    stored_message[3] += active_response[3]  # Append SMS content to existing message
                    stored_message[0].append(active_response[0][0])  # Append SMS ID to list of IDs
    return messages
            

print(parse_response(response))
