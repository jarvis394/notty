#!/usr/bin/env python
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from datetime import datetime
from notty.lib.db import Notes

def main():
    db = Notes()
    bottom_toolbar = HTML('Press <style color="cyan"><b>Ctrl-S</b></style> to save a note and <style color="cyan"><b>Ctrl-C</b></style> to exit.')
    kb = KeyBindings()

    @kb.add('c-q')
    def _(e):
        print('\nExiting...')
        e.app.exit()

    def get_date():
        return datetime.today().strftime('%c')

    def prompt_continuation(width, line_number, wrap_count):
        align = ''
        if line_number < 9: align = '  '
        elif line_number < 99: align = ' '

        if wrap_count > 0:
            return HTML('<style color="gray">     │ </style>')
        else:
            return HTML(f'<style color="gray"> {align}{line_number + 1} │ <style>')

    def prompt_title():
        return prompt(
            HTML('Set a <b><style color="cyan">title</style></b> to the note <style color="gray">(default is current date)</style>: '),
            bottom_toolbar=bottom_toolbar,
            key_bindings=kb
        )

    def prompt_text():
        return prompt(
            HTML('Write some <b><style color="cyan">text</style></b> to the note: \n\n   1 │ '),
            bottom_toolbar=bottom_toolbar,
            multiline=True,
            prompt_continuation=prompt_continuation,
            mouse_support=True,
            key_bindings=kb
        )

    def run():
        print('\n\n')

        title = prompt_title()
        text = prompt_text()

        if title == '': title = get_date()

        pass

    run()
