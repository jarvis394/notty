from asyncio import Future
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import (
    Button,
    Dialog,
    Label
)
from prompt_toolkit.layout.containers import HSplit

class ConfirmationDialog:
    def __init__(self, title, text, yes_text, no_text):
        self.future = Future()

        def yes_handler():
            self.future.set_result(True)

        def no_handler():
            self.future.set_result(None)

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=text),]),
            buttons=[
                Button(text=yes_text, handler=yes_handler),
                Button(text=no_text, handler=no_handler),
            ],
            width=D(preferred=50),
            modal=True
        )

    def __pt_container__(self):
        return self.dialog
