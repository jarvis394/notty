import sqlite3
import appdirs
import os


class Notes:
    def __init__(self):
        self.dirpath = os.path.join(appdirs.user_data_dir(), 'notty')
        self.path = os.path.join(self.dirpath, 'main.db')

        if not os.path.exists(self.dirpath):
            os.makedirs(self.dirpath)

        self.connection = sqlite3.connect(self.path, check_same_thread=False)
        self.db = self.connection.cursor()

        # Init the DB tables
        self.db.execute('''CREATE TABLE IF NOT EXISTS notes
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, title text NOT_NULL, text text NOT_NULL, ts text NOT_NULL);
                   ''')

    def get_all(self):
        data = self.db.execute('SELECT * FROM notes;')
        data = data.fetchall()
        res = []

        for entry in data:
            res.append({'id': entry[0], 'title': entry[1],
                        'text': entry[2], 'ts': entry[3]})
        return res

    def get(self, id):
        data = self.db.execute(f'SELECT * FROM notes WHERE id = {id};')
        data = data.fetchone()
        return {'id': data[0], 'title': data[1], 'text': data[2], 'ts': data[3]}

    def insert(self, data):
        self.db.execute(
            f'INSERT INTO notes (title, text, ts) VALUES (?, ?, ?);', data)
        self.connection.commit()
        return self

    def update_text(self, id, text):
        self.db.execute(f'UPDATE notes SET text = "{text}" WHERE id = {id};')
        self.connection.commit()
        return self

    def update_title(self, id, title):
        self.db.execute(f'UPDATE notes SET title = "{title}" WHERE id = {id};')
        self.connection.commit()
        return self

    def delete(self, id):
        self.db.execute(f'DELETE FROM notes WHERE id = {id}')
        self.connection.commit()
        return self

    def close_conn(self):
        return self.connection.close()
