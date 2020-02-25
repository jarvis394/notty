from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import TextArea, Button
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.application.current import get_app
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign, Float, FloatContainer
from notty.lib.db import Notes
from notty.utils.date_now import date_now
from colorama import Fore, Style
from prompt_toolkit.styles import Style as PromptStyle
from notty.lib.TextInputDialog import TextInputDialog
from notty.lib.ConfirmationDialog import ConfirmationDialog
from notty.lib.MessageDialog import MessageDialog
from notty.lib.db import Notes
import asyncio

RS = Style.RESET_ALL
NOW = date_now()


class ApplicationState:
    title = NOW
    note_id = None
    is_float_displaying = False
    is_saved = False
    notification_text = None

    async def show_notification(self, message: str, timeout: int):
        """
        Shows notification in the reserved space for `timeout` and then hides

        :param message: Message to display
        :param timeout: Timeout
        """
        self.notification_text = HTML(
            f"<style bg=\"white\" color=\"black\">[ {message} ]</style>")
        await asyncio.sleep(timeout)
        self.notification_text = None


db = Notes()
state = ApplicationState()
style = PromptStyle.from_dict(
    {
        "dim": "#444",
        "bold": "bold",
        "status": "reverse",
        "topbar": "bg:#fff bg:blue",
        "line": "#fff",
        "notification": "#fff"
    }
)


def abort():
    app = get_app()
    if get_app().is_running:
        print()
        print(f'  {Fore.YELLOW}Aborting.{RS}')
        print()

        try:
            db.close_conn()
        except Exception as e:
            exception = Exception(f'Exception occurred on exiting: {e}')
            return app.exit(exception=exception)
        return app.exit()


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


def get_topbar_text():
    return [("class:bold", "New note")]


def get_statusbar_upper_text():
    return state.notification_text or state.title


def get_statusbar_right_text():
    return " {}:{}  ".format(
        text_window.document.cursor_position_row + 1,
        text_window.document.cursor_position_col + 1,
    )


# Global key bindings
kb = KeyBindings()

top_bar = Window(
    height=1,
    content=FormattedTextControl(get_topbar_text),
    align=WindowAlign.CENTER,
    style="class:topbar"
)
text_window = TextArea(
    text="",
    multiline=True,
    wrap_lines=True,
    focusable=True,
    scrollbar=True,
    line_numbers=True
)
title_bar = Window(
    FormattedTextControl(get_statusbar_upper_text),
    align=WindowAlign.CENTER,
    style="class:notification",
    height=1
)
status_bar = VSplit([
    Window(
        FormattedTextControl(HTML(
            'Press <style bg="blue"><b>F2</b></style> or <style bg="blue"><b>Ctrl-R</b></style> to set a title')),
        style="class:status"
    ),
    Window(
        FormattedTextControl(get_statusbar_right_text),
        style="class:status.right, bold",
        width=9,
        align=WindowAlign.RIGHT,
    )],
    height=1
)

root_container = FloatContainer(
    HSplit([
        top_bar,
        text_window,
        title_bar,
        status_bar
    ]),
    floats=[]
)
layout = Layout(container=root_container, focused_element=text_window)


@kb.add("c-x", eager=True)
@kb.add("c-c", eager=True)
def _(event):
    " Quit application "
    async def coroutine():
        current_text = text_window.text

        def save_handler(s):
            if state.note_id:
                db.update_text(state.note_id, current_text)
            else:
                db.insert((state.title, current_text, NOW))
            s.future.set_result(True)

        if not state.is_saved:
            dialog = ConfirmationDialog(
                title="Exit",
                text="Exit without saving?",
                yes_text="Yes",
                no_text="Cancel",
                button=('Save', save_handler)
            )
            res = await show_dialog_as_float(dialog)

            # If canceled then do not exit the app
            #
            # We should close the app when clicked "Save" button
            # but we don't need another handler because there's already
            # "save_handler()" attached
            #
            # On "Exit", we should ignore it because abort() function is
            # called right after the "if" statement
            if not res:
                return False

        return abort()

    # Run coroutine
    return asyncio.ensure_future(coroutine())


@kb.add("c-s", eager=True)
def _(event):
    if state.is_saved:
        return False

    if state.note_id:
        db.update_text(state.note_id, text_window.text)
    else:
        db.insert((state.title, text_window.text, NOW))
        state.note_id = db.db.lastrowid

    state.is_saved = True
    asyncio.create_task(state.show_notification("Saved the note", 1.5))


@kb.add("c-r", eager=True)
@kb.add("f2", eager=True)
def _(event):
    " Rename the note "
    async def coroutine():
        dialog = TextInputDialog(title="Rename")
        new_title = await show_dialog_as_float(dialog)

        # Return if no title was entered
        if not new_title or (new_title and new_title.strip() == ''):
            return None

        state.title = new_title.strip()
        state.is_saved = False
        return True

    # Run coroutine
    return asyncio.ensure_future(coroutine())


def on_text_change_handler(e: "TextChange"):
    """ Text change handler """
    if state.is_saved:
        state.is_saved = False


text_window.buffer.on_text_changed.add_handler(on_text_change_handler)

# Build a main application object
application = Application(
    layout=layout,
    key_bindings=kb,
    full_screen=True,
    erase_when_done=False,
    style=style,
    refresh_interval=0.5
)


def execute():
    async def main():
        return await application.run_async()

    return asyncio.run(main())
