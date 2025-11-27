import threading
from nicegui import app, ui
import main_sms
from pages.theme import frame, check_timeout
from functions.encryption_functions import check_hash   

def content():
    # Start the chatbot service
    def start_bot():
        check_timeout(True)  # Reset timeout timer
        
        # Get stored password from tab storage
        password = app.storage.tab.get('password', '')
        
        # Start thread and pass password for whitelist decryption
        threading.Thread(target=main_sms.start_service, args=(password,)).start() # start in new thread
        return
    
    # Stop the chatbot service
    def stop_bot():
        check_timeout(True)  # Reset timeout timer
        main_sms.stop_service()
        return
    

    # Main content within the themed frame
    with frame('Home'):
        ui.label('Welcome to BluChat').classes('text-2xl mt-2')
        with ui.row().classes('w-full no-wrap gap-0'):
            start_button = ui.button('Start Chatbot', on_click=start_bot, color='green').classes('mt-4')
            stop_button = ui.button('Stop Chatbot', on_click=stop_bot, color='red').classes('mt-4 ml-4')
        home_log = ui.log(max_lines=100).classes('mt-4 h-100 w-full')
        
        main_sms.console_log.add(home_log) # Add home_log to shared console log
        ui.context.client.on_disconnect(lambda: main_sms.console_log.remove(home_log)) # Remove on disconnect
    
    
        
