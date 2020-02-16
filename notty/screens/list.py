#!/usr/bin/env python
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings, ConditionalKeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign, ScrollOffsets, Float, FloatContainer
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
from notty.lib.MessageDialog import MessageDialog
from notty.lib.TextInputDialog import TextInputDialog
from notty.utils.date_now import date_now
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
    notification_text = ''
    is_float_displaying = False

    async def show_notification(self, message, timeout):
        self.notification_text = HTML(f"<style bg='white'>{message}</style>")
        await asyncio.sleep(timeout)
        self.notification_text = ''


db = Notes()  # Database class
borders = Border()
sidebar_bindings = KeyBindings()
focus_bindings = KeyBindings()
kb = KeyBindings()
notes = list(reversed(db.get_all()))  # All stored notes
state = ApplicationState()
style = PromptStyle.from_dict(
    {
        "dim": "#444",
        "bold": "bold",
        "sidebar": "bg:#000000",
        "sidebar.label": "bg:#000 #aaa",
        "sidebar.label selected": "bg:#000 #fff bold",
        "sidebar.label seldim": "bg:#444 #fff bold",
        "status": "reverse",
        "topbar": "bg:#fff bg:blue",
        "notification": "#000"
    }
)

# If no notes in DB then append a fake one to the cache with a custom flag
if len(notes) == 0: notes.append({
    'id': 0,
    'title': date_now(),
    'text': '',
    'ts': date_now(),
    '_INSERT_FLAG': True
})


# Key bindings


@kb.add("c-c", eager=True)
@kb.add("c-x", eager=True)
def _(event: KeyPressEvent):
    try:
        db.close_conn()
    except:
        event.app.exit()
    event.app.exit()

@kb.add("f1", eager=True)
def _(event: KeyPressEvent):
    help = HTML("""
        <b>Key combinations:</b>
            F1 - show this text
            F2 - rename the title of current note
            Ctrl-C - exit the application
            Ctrl-S - save the current note
            Ctrl-N - create a new note
            Ctrl-D - delete the current note
            Tab / Shift-Tab - focus next / previous window

            All dangerous operations shows a confirmation dialog.

        <b>File States:</b>
            <style color="white" bg="green"> U </style> - newly created file, needs save
    """)
    show_message("Help", help)

@kb.add("f2", eager=True)
def _(event: KeyPressEvent):
    async def coroutine():
        dialog = TextInputDialog(title="Rename")
        new_title = await show_dialog_as_float(dialog)

        if not state.current_note.get('_INSERT_FLAG'):
            db.update_title(state.current_note['id'], new_title)
        notes[state.selected_option_index]['title'] = new_title

    asyncio.ensure_future(coroutine())

@kb.add("c-n", eager=True)
def _(event: KeyPressEvent):
    notes.insert(0, {
        'title': date_now(),
        'text': '',
        'ts': date_now(),
        '_INSERT_FLAG': True
    })
    update_text_window(0)

def focus_window(event: KeyPressEvent):
    """ Focus next window (in range of two: `sidebar` and `text_window`) and updates the application state """
    get_app().layout.focus(
        text_window if event.app.layout.current_window == sidebar else sidebar)
    state.focused_window = event.app.layout.current_window


@focus_bindings.add("tab", eager=True)
@focus_bindings.add("s-tab", eager=True)
def _(event: KeyPressEvent):
    focus_window(event)


@kb.add("c-s", eager=True)
def _(event: KeyPressEvent):
    text = text_window.document.text

    if state.current_note.get('_INSERT_FLAG'):
        db.insert((state.current_note['title'], state.current_note['text'], state.current_note['ts']))
    else:
        db.update_text(state.current_note['id'], text)

    notes[state.selected_option_index]['text'] = text
    asyncio.create_task(state.show_notification("[ Saved the note ]", 1.5))


# Getters for windows' texts

def get_titlebar_text():
    return [("class:bold", "Notes")]

def get_current_note_title():
    if state.current_note:
        return state.current_note.get('title')
    else:
        return ''

def get_notification_text():
    return state.notification_text

def get_statusbar_text():
    return HTML(" [F1] Help ")

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
    text_window.text = notes[i].get('text')

def show_message(title, text):
    async def coroutine():
        dialog = MessageDialog(title, text)
        await show_dialog_as_float(dialog)

    if not state.is_float_displaying: asyncio.ensure_future(coroutine())


async def show_dialog_as_float(dialog):
    " Coroutine. "
    float_ = Float(content=dialog)
    root_container.floats.insert(0, float_)

    app = get_app()

    focused_before = app.layout.current_window
    app.layout.focus(dialog)
    state.is_float_displaying = True
    result = await dialog.future
    state.is_float_displaying = False
    app.layout.focus(focused_before)

    if float_ in root_container.floats:
        root_container.floats.remove(float_)

    return result

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
                update_text_window(index)

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

            sel = ",selected" if selected and state.focused_window == sidebar else ",seldim" if selected else ""

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

        return tokens

    class Control(FormattedTextControl):
        def move_cursor_down(self):
            state.selected_option_index += 1

        def move_cursor_up(self):
            state.selected_option_index -= 1

    return Window(
        content=Control(get_text_fragments, focusable=True, show_cursor=True),
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
    Window(
        content=FormattedTextControl(get_notification_text),
        height=1,
        style="class:notification",
        align=WindowAlign.CENTER
    ),
    VSplit([
        Window(
            FormattedTextControl(get_statusbar_text),
            style="class:status",
            width=11
        ),
        Window(
            FormattedTextControl(get_current_note_title),
            align=WindowAlign.CENTER,
            style="class:status"
        ),
        Window(
            FormattedTextControl(get_statusbar_right_text),
            style="class:status.right, bold",
            width=9,
            align=WindowAlign.RIGHT,
        )],
        height=1
    ),
])
root_container = FloatContainer(HSplit(
    [
        Window(
            height=1,
            content=FormattedTextControl(get_titlebar_text),
            align=WindowAlign.CENTER,
            style="class:topbar"
        ),
        body,
    ]),
    floats=[]
)
application = Application(
    layout=Layout(root_container, focused_element=sidebar),
    key_bindings=merge_key_bindings([
        kb,
        ConditionalKeyBindings(
            key_bindings=focus_bindings,
            filter=Condition(
                lambda: not state.is_float_displaying)
        ),
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
        state.focused_window = sidebar
        await application.run_async()

    asyncio.run(main())
