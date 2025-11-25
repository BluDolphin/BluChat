import threading
from nicegui import ui
import main_sms
from pages.theme import frame
from pages.login import check_password

def content():
    def start_bot(input_password):
        if not check_password(input_password):
            return ui.notify('Incorrect password', color='red')
        
        threading.Thread(target=main_sms.start_service, args=(input_password,)).start() # start in new thread
        start_bot_dialog.close() # Close dialog
        return
    def stop_bot():
        main_sms.stop_service()
        return
    
    with ui.dialog() as start_bot_dialog, ui.card():
        ui.label('Start Chatbot Service').classes('text-lg mt-2')
        hash_key_input = ui.input('Enter password:', password=True)
        with ui.row().classes('justify-end mt-4 mb-2'):
            ui.button('Close', on_click=start_bot_dialog.close)
            ui.button('Start', on_click=lambda: start_bot(hash_key_input.value)).classes('ml-2')

        
    with frame('Home'):
        ui.label('Welcome to BluChat').classes('text-2xl mt-2')
        with ui.row().classes('w-full no-wrap gap-0'):
            start_button = ui.button('Start Chatbot', on_click=start_bot_dialog.open).classes('mt-4')
            stop_button = ui.button('Stop Chatbot', on_click=stop_bot).classes('mt-4 ml-4')
        running_log = ui.log().classes('mt-4 h-100 w-full')
    
    
        
