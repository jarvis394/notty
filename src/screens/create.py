#!/usr/bin/env python
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from lib.db import Notes
from utils.date_now import date_now
from colorama import Fore, Style

RS = Style.RESET_ALL


def execute():
    """Main execution function"""

    # Notes database
    db = Notes()

    # Bottom toolbar HTML text
    bottom_toolbar = HTML(
        'Press <style bg="blue"><b>Esc-Enter</b></style> to save a note and <style bg="blue"><b>Ctrl-C</b></style> to exit.')

    # Key bindings for letting a user to exit
    kb = KeyBindings()

    # Current date
    DATE_NOW = date_now()

    def prompt_continuation(width, line_number, wrap_count):
        align = ''
        if line_number < 9:
            align = '  '
        elif line_number < 99:
            align = ' '

        if wrap_count > 0:
            return HTML('<style color="gray">     │ </style>')
        else:
            return HTML(f'<style color="gray"> {align}{line_number + 1} │ </style>')

    def prompt_title():
        return prompt(
            HTML('Set a <b><style color="blue">title</style></b> to the note <style color="gray">(default is current date)</style>: '),
            bottom_toolbar=bottom_toolbar,
            key_bindings=kb
        )

    def prompt_text():
        return prompt(
            HTML(
                'Write some <b><style color="blue">text</style></b> to the note: \n\n<style color="gray">   1 │ </style>'),
            bottom_toolbar=bottom_toolbar,
            multiline=True,
            prompt_continuation=prompt_continuation,
            mouse_support=True,
            key_bindings=kb
        )

    try:
        title = prompt_title()
        text = prompt_text().strip()
    except KeyboardInterrupt:
        print(f'\n  {Fore.YELLOW}Aborting.{RS}\n')
        return

    if title == '':
        title = DATE_NOW

    if text == '':
        print(f'\n\n   No text was found, {Fore.YELLOW}aborting{RS}. \n')
        return

    # Write DB entry
    
    
    print(HTML(f'<style color="blue">Successfully wrote your note to the storage with an ID {id}</style>'))

    return [title, text, DATE_NOW]
