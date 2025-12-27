from nicegui import ui, app
from contextlib import contextmanager
from functions.check_timeout import check_timeout

COLOUR_BG = '0d1331'  # Very dark blue for background
COLOUR_1 = '151b3e'  # Dark blue for sidebar
COLOUR_2 = '152851'  # Medium blue for highlights


# context manager for page layout with sidebar and theming
@contextmanager 
def frame(current_page):
    # Remove default padding and margins from the page and body
    ui.add_head_html('''
        <style>
            body { margin: 0; padding: 0; }
            .nicegui-content { padding: 0 !important; margin: 0 !important; max-width: none !important; }
        </style>
    ''')
    
    check_timeout(True) # Check for session timeout & reset timer
            
    # Create a full-height row to hold sidebar and main content
    with ui.row().classes('h-screen w-full no-wrap gap-0') as layout_container:
        # Timer to check periodically (In main window to fix navigation)
        # Safe wrapper to ensure layout_container is accessible
        
        ui.timer(10.0, lambda: check_timeout()) # Check for timeout every 10 seconds
        
        # Sidebar: COLOUR_1, full height, width 64, padding 4
        with ui.column().style(f'background-color: #{COLOUR_1}').classes('w-64 h-full p-4 overflow-y-auto'):
            # Sidebar Title
            ui.label('Menu').classes('text-xl font-bold mb-4 text-white') 
            
            # Helper function to create navigation links with highlighting
            def nav_link(name, target):
                # Base classes: block for full width, padding, rounded corners
                classes = f'mb-2 w-full block p-2 rounded hover:text-white hover:bg-[#{COLOUR_2}]'
                if name == current_page:
                    # Active style: lighter background, white text
                    classes += f' bg-[#{COLOUR_2}] text-white'
                ui.link(name, target).classes(classes)

            # Navigation links
            nav_link('Home', '/home')
            nav_link('Whitelist', '/whitelist')
            nav_link('Settings', '/settings')
        
        # Main Content Area
        with ui.column().style(f'background-color: #{COLOUR_BG}').classes('p-4 flex-1 h-full text-white overflow-y-auto overflow-x-auto'):
            yield  # Pause here to inject content into the main area
