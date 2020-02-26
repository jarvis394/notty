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


def get_ids(ctx, args, incomplete):
    notes = db.get_all()
    completions = list(map(lambda k: k["id"], notes))
    return [k for k in completions if incomplete in k]


@click.group(cls=ClickAliasedGroup)
def cli():
    """
    Fast terminal-based notes application

    Storage is located in the system's default app_dir. SQLite3 is used to store and process your notes.
    """
    pass

@cli.command(aliases=['edit', 'e'], help='Edits a note in your default editor')
@click.argument('id', type=click.INT, autocompletion=get_ids)
@click.option('--editor', '-e')
def edit(id, editor):
    note = db.get(id)

    if not note:
        return click.echo(f"\n\n  Note with ID {Fore.YELLOW}{id}{RS} was not found\n")

    try:
        new_text = click.edit(text=note.get('text'), editor=editor)
    except Exception as e:
        print(f'On trying to edit: {e}')
        return
    db.update_text(id, new_text)
    click.echo(f"\n\n  Note with ID {Fore.YELLOW}{id}{RS} was successfully saved!\n")

@cli.command(aliases=['create', 'c'], help='Creates a new note')
def create():
    return screens.create.execute()

@cli.command(aliases=['list', 'l'], help='Lists your notes in a cool fancy window')
@click.argument('id', type=int, required=False, default=None)
@click.option('--no-window', '-n', default=False, is_flag=True, help='print your notes as a list without showing a fancy window')
def list(no_window, id):
    if no_window or id:
        def format_note(note):
            id, title, text, ts = note["id"], note["title"], note["text"], note["ts"]
            formatted_text = '\n    '.join(text.strip().split('\n'))[:96] + ('...' if len(text) > 96 else '')
            return '\n'.join([
                f"{Fore.YELLOW}[{id}]{RS} {Style.BRIGHT}{Fore.CYAN}{title}{RS}",
                f"{Style.DIM}Date: {ts}{RS}",
                f"\n    {formatted_text}\n\n"
            ])

        notes = reversed(db.get_all())
        notes = map(format_note, notes)
        click.echo_via_pager(notes)
    else:
        return screens.list.execute()

# Initialize color support
colorama.init()

def main():
    cli()

if __name__ == "__main__":
    main()
