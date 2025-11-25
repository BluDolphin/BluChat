from nicegui import ui
from contextlib import contextmanager

colour_bg = '0d1331'  # Very dark blue
colour_1 = '151b3e'  # Dark blue
colour_2 = '152851'  # Medium blue

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

    # Create a full-height row to hold sidebar and main content
    with ui.row().classes('h-screen w-full no-wrap gap-0'):
        # Sidebar: colour_1, full height, width 64, padding 4
        with ui.column().style(f'background-color: #{colour_1}').classes('w-64 h-full p-4'):
            # Sidebar Title
            ui.label('Menu').classes('text-xl font-bold mb-4 text-white') 
            
            # Helper function to create navigation links with highlighting
            def nav_link(name, target):
                # Base classes: block for full width, padding, rounded corners
                classes = f'mb-2 w-full block p-2 rounded hover:text-white hover:bg-[#{colour_2}]'
                if name == current_page:
                    # Active style: lighter background, white text
                    classes += f' bg-[#{colour_2}] text-white'
                ui.link(name, target).classes(classes)

            nav_link('Home', '/home')
            nav_link('Settings', '/settings')
        
        # Main Content Area
        with ui.column().style(f'background-color: #{colour_bg}').classes('p-4 w-full h-full text-white'):
            yield  # Pause here to inject content into the main area
