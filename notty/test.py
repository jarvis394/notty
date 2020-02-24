#!/usr/bin/env python
"""
A simple example of a a text area displaying "Hello World!".
"""
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import Frame, TextArea, Box
from prompt_toolkit.formatted_text import HTML, ANSI
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window
from mdv import main as mdv

text = FormattedTextControl(
    ANSI(mdv("# Hello world!\nPress control-c to quit."))
)


# Layout for displaying hello world.
# (The frame creates the border, the box takes care of the margin/padding.)
root_container = Frame(
    TextArea(Window(text))
)
layout = Layout(container=root_container)


# Key bindings.
kb = KeyBindings()


@kb.add("c-c")
def _(event):
    " Quit when control-c is pressed. "
    event.app.exit()


# Build a main application object.
application = Application(layout=layout, key_bindings=kb, full_screen=True)


def main():
    application.run()


if __name__ == "__main__":
    main()
