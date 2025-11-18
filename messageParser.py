with open('responeMulti.txt', 'r') as file:
    response = file.read()


import datetime, logging

logging.basicConfig(level=logging.INFO)
 
def parse_response(response):
    
    response_lines = response.splitlines()
    
    # data is stored nested as [list of message IDs, Sender, UnixTime, ResponseContent]
    messages = [[[], '', 0, ""]]  # Initialize with a dummy entry to handle multi-part messages
    
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
            
            logging.debug('Cleaned message data: %s', message_list)
            
            
            # Dealing with multi SMS messages
            for message in messages:
                # If timestamp is within 5 seconds and matching sender
                if message[1] == message_list[1] and int(message[2]) <= int(message_list[2]) <= int(message[2]) + 5:  
                        logging.debug('Multi message found, appending content.')
                        message[3] += message_list[3]  # Append content
                        message[0].append(message_list[0][0])  # Append message ID
                        
                        break # Skip appending new entry and pointless iterations
                
                if message == messages[-1]:  # If reached the last message without matches
                    messages.append(message_list)
                    break

    return messages
            

print(parse_response(response))
