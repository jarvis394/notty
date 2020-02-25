import click
import colorama
import notty.screens as screens
from notty.lib.CommandAliases import ClickAliasedGroup
from notty.lib.db import Notes
from notty.utils.date_now import date_now
import os
from colorama import Fore, Back, Style


NOW = date_now()
RS = Style.RESET_ALL
db = Notes()

def clear():
    return os.system('clear')

@click.group(cls=ClickAliasedGroup)
def cli():
    pass

@cli.command(aliases=['edit', 'e'], help='edits a note in your default editor')
@click.argument('id')
def edit(id):
    note = db.get(id)

    if not note:
        return click.echo(f"\n\n  Note with ID {Fore.YELLOW}{id}{RS} was not found\n")
    new_text = click.edit(text=note.get('text'))
    db.update_text(id, new_text)
    click.echo(f"\n\n  Note with ID {Fore.YELLOW}{id}{RS} was successfully saved!\n")

@cli.command(aliases=['create', 'c'], help='creates a new note')
def create():
    return screens.create.execute()

@cli.command(aliases=['list', 'l'], help='lists your notes in a cool fancy window')
def list():
    return screens.list.execute()

# Initialize color support
colorama.init()

def main():
    cli()

if __name__ == "__main__":
    main()
