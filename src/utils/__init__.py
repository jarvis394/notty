import appdirs
import sqlite3

DATA_PATH = appdirs.user_data_dir()
conn = sqlite3.connect('notty.db')
cursor = conn.cursor()

def init():
    return cursor.execute('''CREATE TABLE IF NOT EXISTS notes
                   (id integer primary key, title text, text text, ts text);
                   ''')

def save_data(data):
    return cursor.execute(f'INSERT INTO notes VALUES (?, ?, ?, ?);', data)

def get_data(id):
    data = cursor.execute(f'SELECT * FROM notes WHERE id = {id};')
    return data.fetchone()

def get_all_data():
    data = cursor.execute(f'SELECT * FROM notes;')
    return data.fetchall()

def db_conn_close():
    return cursor.close()

init()
