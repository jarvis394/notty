import click
import colorama
import notty.screens as screens
from notty.lib.CommandAliases import ClickAliasedGroup
import os
from colorama import Fore, Back, Style

def clear():
    return os.system('clear')

@click.group(cls=ClickAliasedGroup)
def cli():
    pass

@cli.command(aliases=['create', 'c'], help='creates a new note')
def create():
    return screens.create.execute()

@cli.command(aliases=['list', 'l'], help='lists your notes in a cool fancy window')
def list():
    return screens.list.execute()

# Initialize color support
colorama.init()

# Reset style string
RS = Style.RESET_ALL

if __name__ == "__main__":
    cli()
