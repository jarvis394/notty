#!/usr/bin/env python
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings, ConditionalKeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign, ScrollOffsets, Float, FloatContainer
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.formatted_text import HTML, ANSI
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.shortcuts import yes_no_dialog, message_dialog, input_dialog
from prompt_toolkit.styles import Style as PromptStyle
from prompt_toolkit.utils import Event
from prompt_toolkit.widgets.base import Border
from prompt_toolkit.widgets import TextArea, SearchToolbar
from prompt_toolkit.application.current import get_app
from prompt_toolkit.filters import Condition
from colorama import Fore, Style
from notty.lib.db import Notes
from notty.lib.MessageDialog import MessageDialog
from notty.lib.TextInputDialog import TextInputDialog
from notty.lib.ConfirmationDialog import ConfirmationDialog
from notty.utils.date_now import date_now
from notty.utils.if_mousedown import if_mousedown
import asyncio
import threading


MAX_TITLE_LENGTH = 36
SAVING_INTERVAL = 60  # Once a minute


class ApplicationState:
    """
    Application state
    """

    """ Current selected option index (in notes List) """
    selected_option_index = 0

    """ Current note object """
    current_note = None

    """ Current note text """
    current_text = ''

    """ Current focused window """
    focused_window = None

    """
    Notification text to display
    Used in self.show_notification
    """
    notification_text = ''

    """
    State which describes if any float is displaying currently
    Needed for disabling any <Tab> key bindings for windows when a float is displaying
    """
    is_float_displaying = False

    _save_job_timer = None

    async def show_notification(self, message: str, timeout: int):
        """
        Shows notification in the reserved space for `timeout` and then hides

        :param message: Message to display
        :param timeout: Timeout
        """
        self.notification_text = HTML(f"<style bg='white'>{message}</style>")
        await asyncio.sleep(timeout)
        self.notification_text = ''


# Database class
db = Notes()

# Useful borders. Used in Layout
borders = Border()

# Key bindings for the sidebar
sidebar_bindings = KeyBindings()

# Key bindings for focusing windows
focus_bindings = KeyBindings()

# Global keybindings
kb = KeyBindings()

# All stored notes
notes = list(reversed(db.get_all()))

# Application state
state = ApplicationState()

# Application styles
style = PromptStyle.from_dict(
    {
        "dim": "#444",
        "bold": "bold",
        "sidebar.label": "#aaa",
        "sidebar.label selected": "#fff bold",
        "sidebar.label seldim": "bg:#444 #fff bold",
        "sidebar.modified": "bg:orange white bold",
        "status": "reverse",
        "topbar": "bg:#fff bg:blue",
        "notification": "#000"
    }
)

# Text editor
text_window = TextArea(
    text=state.current_text,
    scrollbar=True,
    line_numbers=True,
    multiline=True,
    width=Dimension(min=24),
    focus_on_click=True
)

# If no notes in DB then append a fake one to the cache with a custom flag
if len(notes) == 0:
    notes.append({
        'id': 0,
        'title': date_now(),
        'text': '',
        'ts': date_now(),
        '_INSERT_FLAG': True
    })


def save_current_note():
    """ Save the current note """
    text = text_window.document.text or ''

    if not state.current_note: return

    if state.current_note.get('_INSERT_FLAG'):
        db.insert((state.current_note['title'],
                   text, state.current_note['ts']))
    else:
        db.update_text(state.current_note['id'], text)

    notes[state.selected_option_index]['text'] = text
    pass


#### Key bindings ####

@kb.add("c-c", eager=True)
@kb.add("c-x", eager=True)
def _(event: KeyPressEvent):
    """ Exit the application """
    state._save_job_timer.cancel()
    try:
        # Try saving current note
        # We do not try to save other notes, because they are already saved
        # when user switches the current note
        save_current_note()

        # Try to close SQLite DB connection
        db.close_conn()
    except Exception as e:
        exception = Exception(
            f'Exception occurred on exiting: {e}')
        return event.app.exit(exception=exception)
    else:
        return event.app.exit()


@kb.add("f1", eager=True)
def _(event: KeyPressEvent):
    """ Show help float to the user """
    help = HTML(f"""
        <b>Key combinations:</b>
            F1 - show this text
            F2 - rename the title of current note
            Ctrl-C - exit the application
            Ctrl-N - create a new note
            Ctrl-D - delete the current note
            Tab / Shift-Tab - focus next / previous window

            <i>All dangerous operations shows a confirmation dialog.</i>
            Notes are being saved in the interval of {SAVING_INTERVAL} seconds.
    """)
    return show_message("Help", help)


@kb.add("f2", eager=True)
def _(event: KeyPressEvent):
    """ Renames the current note """
    async def coroutine():
        dialog = TextInputDialog(title="Rename")
        new_title = await show_dialog_as_float(dialog)

        # Return if no title was entered
        if not new_title:
            return

        # If no custom flag, then update the title directly in DB
        # If the current note is located only in cache (notes List),
        # then there wouldn't be any document to update (tl;dr; will cause SQLite error)
        if not state.current_note.get('_INSERT_FLAG'):
            db.update_title(state.current_note['id'], new_title)
        notes[state.selected_option_index]['title'] = new_title

    # Run coroutine
    return asyncio.ensure_future(coroutine())


@kb.add("c-d", eager=True)
def _(event: KeyPressEvent):
    """ Deletes the current note """
    async def coroutine():
        dialog = ConfirmationDialog(title="Rename", yes_text="Delete", no_text="Cancel", text="Delete?")
        result = await show_dialog_as_float(dialog)

        # Return if canceled
        if not result:
            return

        if not state.current_note.get('_INSERT_FLAG'):
            db.delete(state.current_note.get("id"))
        del notes[state.selected_option_index]

        i = state.selected_option_index
        if len(notes) - 1 < i:
            i = i - 1
        update_text_window(i)

        # If no notes in DB then append a fake one to the cache with a custom flag
        if len(notes) == 0:
            notes.append({
                'id': 0,
                'title': date_now(),
                'text': '',
                'ts': date_now(),
                '_INSERT_FLAG': True
            })

            update_text_window(0)
            state.selected_option_index = 0
            event.app.layout.focus(text_window)

    # Run coroutine
    return asyncio.ensure_future(coroutine())


@kb.add("c-t", eager=True)
def _(event: KeyPressEvent):
    """ Show the time of note creation """
    ts = f'[ {state.current_note.get("ts")} ]'
    asyncio.ensure_future(state.show_notification(ts, 2))


@kb.add("c-n", eager=True)
def _(event: KeyPressEvent):
    """ Create a new note """
    notes.insert(0, {
        'title': date_now(),
        'text': '',
        'ts': date_now(),
        '_INSERT_FLAG': True
    })
    update_text_window(0)
    state.selected_option_index = 0
    event.app.layout.focus(text_window)


@focus_bindings.add("tab", eager=True)
def _(event: KeyPressEvent):
    """ Focuses a next window """
    event.app.layout.focus_next()
    state.focused_window = event.app.layout.current_window


@focus_bindings.add("s-tab", eager=True)
def _(event: KeyPressEvent):
    """ Focuses a previous window """
    event.app.layout.focus_previous()
    state.focused_window = event.app.layout.current_window


@kb.add('c-s')
def _(e: KeyPressEvent):
    " Save manually "
    save_current_note()
    asyncio.create_task(state.show_notification("[ Saved the note ]", 1.5))
    pass


""" Save job """
def save_job():
    state._save_job_timer = threading.Timer(SAVING_INTERVAL, save_job)
    state._save_job_timer.start()

    save_current_note()


# Getters for windows' texts

def get_titlebar_text():
    return [("class:bold", "Notes")]


def get_current_note_title():
    return state.current_note.get('title') or ''


def get_notification_text():
    return state.notification_text


def get_statusbar_text():
    return HTML(" [F1] Help ")


def get_statusbar_right_text():
    return " {}:{}  ".format(
        text_window.document.cursor_position_row + 1,
        text_window.document.cursor_position_col + 1,
    )


# Needed to be called `switch_note()`
def update_text_window(i: int):
    """ Updates a text in text input window """
    state.current_note = notes[i]
    text_window.text = notes[i].get('text')


def show_message(title, text):
    async def coroutine():
        dialog = MessageDialog(title, text)
        await show_dialog_as_float(dialog)

    if not state.is_float_displaying:
        asyncio.ensure_future(coroutine())


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
    Creates the `Layout` for the sidebar with the configurable options.
    """

    def get_text_fragments():
        tokens = []  # List of tokens
        handle = sidebar_bindings.add  # Shortcut for sidebar key bindings

        def append(index, label, is_modified):
            """ Appends new item to the tokens List """
            # Current selected note state
            selected = index == state.selected_option_index

            @if_mousedown
            def select_item(mouse_event):
                """ Select item if it was clicked """
                save_current_note()
                state.selected_option_index = index
                update_text_window(index)

            @handle("up")
            def _(event):
                """ Handles <up> arrow key """
                save_current_note()
                if state.selected_option_index - 1 < 0:
                    state.selected_option_index = len(notes) - 1
                else:
                    state.selected_option_index -= 1
                update_text_window(state.selected_option_index)

            @handle("down")
            def _(event):
                """ Handles <down> arrow key """
                save_current_note()
                if state.selected_option_index + 1 > len(notes) - 1:
                    state.selected_option_index = 0
                else:
                    state.selected_option_index += 1
                update_text_window(state.selected_option_index)

            sel = ",selected" if selected and state.focused_window == sidebar else ",seldim" if selected else ""
            spaces = MAX_TITLE_LENGTH - len(label)

            tokens.append(("class:sidebar.label" + sel, f"{label}{' ' * spaces}", select_item))

            if selected:
                tokens.append(("[SetCursorPosition]", ""))

            tokens.append(("class:sidebar", "\n"))

        i = 0
        for note in notes:
            append(i, note['title'] if len(note['title'])
                   < 32 else note['title'][0:(MAX_TITLE_LENGTH - 3)] + '...', note.get('is_modified'))
            i += 1

        return tokens

    return Window(
        content=FormattedTextControl(get_text_fragments, focusable=True),
        style="class:sidebar",
        width=Dimension(max=36, min=16, preferred=36),
        height=Dimension(min=3),
        always_hide_cursor=True,
        wrap_lines=True,
        scroll_offsets=ScrollOffsets(top=1, bottom=1),
    )


def on_text_change_handler(e: "TextChange"):
    """ Updates the file state """
    pass


on_text_change = Event("TextChange")
on_text_change.add_handler(on_text_change_handler)

sidebar = create_sidebar()
text_window.buffer.on_text_changed = on_text_change
body = HSplit([
    VSplit([
        sidebar,
        Window(width=2, char=f'{borders.VERTICAL} ', style="class:line"),
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
        save_job()
        return await application.run_async()

    return asyncio.run(main())
