import sqlite3

class SQL():
    #создание базы данных
    def create_db(self):
        con = sqlite3.connect('db.sqlite')
        cur = con.cursor()
        con.close()

    def create_table(self):
        con = sqlite3.connect('db.sqlite')
        cur = con.cursor()

        query = '''
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        subject TEXT,
        level TEXT,
        task TEXT,
        answer TEXT);
        '''
        cur.execute(query)
        con.commit()
        con.close()

    #запрос к SQL по критериям
    def update_data(self, user_id, column, value):
        con = sqlite3.connect('db.sqlite')
        cur = con.cursor()

        #column - название поля в таблице users
        query = f'UPDATE users SET {column} = ? WHERE user_id = ?'
        cur.execute(query, (user_id, value, ))
        con.commit()
        con.close()

    #извлечение информации о пользователе
    def select_info(self, user_id):
        con = sqlite3.connect('db.sqlite')
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        query = f'SELECT * FROM users WHERE user_id = ?'
        cur.execute(query, (user_id, ))
        con.close()

    #удаление данных пользователя с таблицы
    def delete(self, user_id):
        con = sqlite3.connect('db.sqlite')
        cur = con.cursor()

        query = f'DELETE * FROM users WHERE user_id = ?'
        cur.execute(query, (user_id,))
        con.commit()
        con.close()

