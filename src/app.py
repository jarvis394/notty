import argparse
import colorama
import screens
import os
from colorama import Fore, Back, Style

# Clear the screen
os.system("clear")

# Initialize color support
colorama.init()

# Reset style string
RS = Style.RESET_ALL

if __name__ == "__main__":
    screens.create.execute()
