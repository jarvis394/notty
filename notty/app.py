import click
import colorama
import screens
from lib.CommandAliases import ClickAliasedGroup
import os
from colorama import Fore, Back, Style

def clear():
    return os.system('clear')

@click.group(cls=ClickAliasedGroup)
def cli():
    pass

@cli.command(aliases=['create', 'c'])
def create():
    clear()
    return screens.create.execute()

@cli.command(aliases=['list', 'l'])
def list():
    clear()
    return screens.list.execute()

# Initialize color support
colorama.init()

# Reset style string
RS = Style.RESET_ALL

if __name__ == "__main__":
    cli()
