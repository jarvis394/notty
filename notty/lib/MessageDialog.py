from asyncio import Future
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import (
    Button,
    Dialog,
    Label,
    TextArea
)
from prompt_toolkit.layout.containers import HSplit

class MessageDialog:
    def __init__(self, title, text):
        self.future = Future()

        def set_done():
            self.future.set_result(None)

        ok_button = Button(text="OK", handler=(lambda: set_done()))

        self.dialog = Dialog(
            title=title,
            body=HSplit([TextArea(text=text, read_only=True, multiline=True, scrollbar=True)]),
            buttons=[ok_button],
            width=D(preferred=80),
            modal=True
        )

    def __pt_container__(self):
        return self.dialog


