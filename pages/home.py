from nicegui import ui
from pages.theme import frame
import main_sms

def content():
    def start_bot():
        main_sms.start_service()
        return
    def stop_bot():
        main_sms.stop_service()
        return
    
    with frame('Home'):
        ui.label('Welcome to BluChat').classes('text-2xl mt-2')
        with ui.row().classes('w-full no-wrap gap-0'):
            start_button = ui.button('Start Chatbot', on_click=start_bot).classes('mt-4')
            stop_button = ui.button('Stop Chatbot', on_click=stop_bot).classes('mt-4 ml-4')
        running_log = ui.log().classes('mt-4 h-100 w-full')
    
    
        
