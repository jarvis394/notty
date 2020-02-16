from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import (
    VSplit,
    Window,
    HSplit
)
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets.base import Border
from prompt_toolkit.widgets import (
    Button,
    MenuContainer,
    MenuItem,
    SearchToolbar,
    TextArea,
)
from prompt_toolkit.search import start_search

kb = KeyBindings()
buffer1 = Buffer()  # Editable buffer.
borders = Border()

search_toolbar = SearchToolbar()
text_field = TextArea(
    scrollbar=True,
    line_numbers=True,
    search_field=search_toolbar,
)

body = VSplit([
    HSplit([
        Window(content=BufferControl(buffer=buffer1)),
    ]),
    Window(width=1, char=borders.VERTICAL),
    HSplit([
        text_field,
        search_toolbar,
    ])
])

root_container = MenuContainer(
    body=body,
    menu_items=[
        MenuItem(
            "File",
            children=[
#                MenuItem("New...", handler=do_new_file),
#                MenuItem("Open...", handler=do_open_file),
                MenuItem("Save"),
                MenuItem("Save as..."),
                MenuItem("-", disabled=True),
                MenuItem("Exit"),
            ],
        ),
    ]
)

layout = Layout(root_container, focused_element=text_field)

@kb.add('c-q')
def exit_(event):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    event.app.exit()

app = Application(layout=layout, full_screen=True, key_bindings=kb)
app.run()
