import threading
from nicegui import ui
import main_sms
from pages.theme import frame, check_timeout
from functions.check_password import check_password

def content():
    # Start the chatbot service
    def start_bot(input_password, home_log):
        check_timeout(True)  # Reset timeout timer
        if not check_password(input_password):
            return ui.notify('Incorrect password', color='red')
        
        threading.Thread(target=main_sms.start_service, args=(input_password, home_log)).start() # start in new thread
        start_bot_dialog.close() # Close dialog
        return
    
    # Stop the chatbot service
    def stop_bot():
        check_timeout(True)  # Reset timeout timer
        main_sms.stop_service()
        return
    
    # Dialog for starting the bot
    with ui.dialog() as start_bot_dialog, ui.card():
        ui.label('Start Chatbot Service').classes('text-lg mt-2') # Dialog title
        hash_key_input = ui.input('Enter password:', password=True) # Input for password
        with ui.row().classes('justify-end mt-4 mb-2'): # Row for buttons
            ui.button('Close', on_click=start_bot_dialog.close) # Close button
            ui.button('Start', on_click=lambda: start_bot(hash_key_input.value, home_log)).classes('ml-2') # Start button
    
    # Main content within the themed frame
    with frame('Home'):
        ui.label('Welcome to BluChat').classes('text-2xl mt-2')
        with ui.row().classes('w-full no-wrap gap-0'):
            start_button = ui.button('Start Chatbot', on_click=start_bot_dialog.open, color='green').classes('mt-4')
            stop_button = ui.button('Stop Chatbot', on_click=stop_bot, color='red').classes('mt-4 ml-4')
        home_log = ui.log(max_lines=100).classes('mt-4 h-100 w-full')
    
    
        
