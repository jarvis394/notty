from datetime import datetime


def date_now(): 
    """Returns current date in UTF format"""
    return datetime.today().strftime('%c')
