import argsparse
import colorama
from colorama import Fore, Back, Style
from datetime import datetime
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout


# Initialize color support
colorama.init()

# Reset style string
RS = Style.RESET_ALL

"""Returns current date in UTF format"""
def date_now(): return datetime.today().strftime('%c')


application = Application(
    layout=Layout(root_container, focused_element=left_window),
    key_bindings=kb,
    # Let's add mouse support!
    mouse_support=True,
    # Using an alternate screen buffer means as much as: "run full screen".
    # It switches the terminal to an alternate screen.
    full_screen=True,
)
