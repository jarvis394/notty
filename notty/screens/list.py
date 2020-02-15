#!/usr/bin/env python
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings, ConditionalKeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign, ScrollOffsets
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.styles import Style as PromptStyle
from prompt_toolkit.widgets.base import Border
from prompt_toolkit.widgets import TextArea, SearchToolbar
from prompt_toolkit.application.current import get_app
from prompt_toolkit.filters import Condition
from colorama import Fore, Style
from notty.lib.db import Notes
from notty.utils.if_mousedown import if_mousedown
import asyncio


class ApplicationState:
    """
    Application state.
    """

    selected_option_index = 0
    current_note = None
    current_text = ''
    focused_window = None
    statusbar_text = None

    async def show_statusbar_message(self, message, timeout):
        self.statusbar_text = message
        await asyncio.sleep(timeout)
        self.statusbar_text = None


db = Notes()  # Database class
borders = Border()
sidebar_bindings = KeyBindings()
kb = KeyBindings()
notes = db.get_all()  # All stored notes
state = ApplicationState()
style = PromptStyle.from_dict(
    {
        "dim": "#444",
        "bold": "bold",
        "sidebar": "bg:#000000",
        "sidebar.label": "bg:#000 #aaa",
        "sidebar.label selected": "bg:#fff #444 bold",
        "status": "reverse",
        "topbar": "bg:#fff bg:blue"
    }
)

# Key bindings


@kb.add("c-c", eager=True)
@kb.add("c-x", eager=True)
def _(event: KeyPressEvent):
    event.app.exit()


def focus_window(event: KeyPressEvent):
    """ Focus  next window (in range of two: `sidebar` and `text_window`) and updates the application state """
    get_app().layout.focus(
        text_window if event.app.layout.current_window == sidebar else sidebar)
    state.focused_window = event.app.layout.current_window


@kb.add("tab", eager=True)
@kb.add("s-tab", eager=True)
def _(event: KeyPressEvent):
    focus_window(event)


@kb.add("c-s", eager=True)
def _(event: KeyPressEvent):
    text = text_window.document.text
    db.update_text(state.current_note['id'], text)
    notes[state.selected_option_index]['text'] = text
    asyncio.create_task(state.show_statusbar_message(" Saved the note! ", 1.5))


# Getters for windows' texts

def get_titlebar_text():
    return [("class:bold", "Notes")]


def get_statusbar_text():
    if not state.statusbar_text:
        return HTML(" Press <style bg='blue'><b>Ctrl-S</b></style> to save the note, <style bg='blue'><b>Ctrl-N</b></style> to create new and <style bg='blue'><b>Ctrl-D</b></style> to delete. ")
    else:
        return state.statusbar_text


def get_statusbar_right_text():
    return " {}:{}  ".format(
        text_window.document.cursor_position_row + 1,
        text_window.document.cursor_position_col + 1,
    )


def update_text_window(i: int):
    """
    Updates the text in text input window
    """
    state.current_note = notes[i]
    text_window.text = notes[i]['text']


def create_sidebar():
    """
    Create the `Layout` for the sidebar with the configurable options.
    """

    def get_text_fragments():
        tokens = []
        handle = sidebar_bindings.add

        def append(index, label):
            selected = index == state.selected_option_index

            @if_mousedown
            def select_item(mouse_event):
                state.selected_option_index = index

            @handle("up")
            def _(event):
                if state.selected_option_index - 1 < 0:
                    state.selected_option_index = len(notes) - 1
                else:
                    state.selected_option_index -= 1
                update_text_window(state.selected_option_index)

            @handle("down")
            def _(event):
                if state.selected_option_index + 1 > len(notes) - 1:
                    state.selected_option_index = 0
                else:
                    state.selected_option_index += 1
                update_text_window(state.selected_option_index)

            sel = ",selected" if selected else ""

            tokens.append(("class:sidebar.label" + sel, "%-36s" %
                           label, select_item))

            if selected:
                tokens.append(("[SetCursorPosition]", ""))

            tokens.append(("class:sidebar", "\n"))

        i = 0
        for note in notes:
            append(i, note['title'] if len(note['title'])
                   < 36 else note['title'][0:32] + '...')
            i += 1

        tokens.pop()  # Remove last newline.

        return tokens

    class Control(FormattedTextControl):
        def move_cursor_down(self):
            state.selected_option_index += 1

        def move_cursor_up(self):
            state.selected_option_index -= 1

    return Window(
        content=Control(get_text_fragments),
        style="class:sidebar",
        width=Dimension.exact(36),
        height=Dimension(min=3),
    )


sidebar = create_sidebar()
text_window = TextArea(text=state.current_text,
                       scrollbar=True, line_numbers=True, multiline=True)
body = HSplit([
    VSplit([
        sidebar,
        Window(width=1, char=borders.VERTICAL, style="class:line"),
        text_window
    ]),
    VSplit([
        Window(FormattedTextControl(get_statusbar_text), style="class:status"),
        Window(
            FormattedTextControl(get_statusbar_right_text),
            style="class:status.right, bold",
            width=9,
            align=WindowAlign.RIGHT,
        )
    ],
        height=1
    ),
])
root_container = HSplit(
    [
        Window(
            height=1,
            content=FormattedTextControl(get_titlebar_text),
            align=WindowAlign.CENTER,
            style="class:topbar"
        ),
        body,
    ]
)
application = Application(
    layout=Layout(root_container, focused_element=sidebar),
    key_bindings=merge_key_bindings([
        kb,
        ConditionalKeyBindings(
            key_bindings=sidebar_bindings,
            filter=Condition(
                lambda: state.focused_window == sidebar)
        )
    ]),
    mouse_support=True,
    full_screen=True,
    style=style,
    refresh_interval=0.5
)

def execute():
    async def main():
        update_text_window(0)
        await application.run_async()

    asyncio.run(main())
    