import pymysql
# later: comment document and fix light warnings
TABLE_NAME = 'User'
CHAR_LEN = 50

db = pymysql.connect(
    host='localhost',
    user='Tester',  # 'GodGamer'
    passwd='Tester@2023',  # 'GodGamerData@2023'
    database='Chat'
)
cursor = db.cursor()
# cursor.execute('CREATE TABLE User (name VARCHAR(50) NOT NULL PRIMARY KEY, pass VARCHAR(50) NOT NULL)')


class DataBaseHandler:
    def __init__(self):
        pass

    @staticmethod
    def adduser(username, password):
        out = DataBaseHandler.check_user(username, password)
        if not out[0] and out[1] != 'Password is incorrect':
            cursor.execute(f'INSERT INTO {TABLE_NAME} (name, pass) VALUES (%s,%s)', (username, password))
            print(f'{username} added')
            db.commit()
            return True, 'Signed up Successfully'
        else:
            print(f'{username} already in use')
            return False, 'Username already in use'

    @staticmethod
    def check_user(username, password):
        cursor.execute(f'SELECT * FROM {TABLE_NAME}')
        for x in cursor:
            if x[0] == username:
                if x[1] == password:
                    return True, 'All credentials correct'
                else:
                    return False, 'Password is incorrect'
        return False, 'No user found, please sign up'

    @staticmethod
    def delete_user(username):
        cursor.execute(f'DELETE FROM {TABLE_NAME} where name = (%s)', (username,))
        print(f'{username} deleted')
        db.commit()

    @staticmethod
    def display_table():
        cursor.execute(f'SELECT * FROM {TABLE_NAME}')
        for x in cursor:
            print(x)

    @staticmethod
    def delete_all():
        cursor.execute(f'SELECT name FROM {TABLE_NAME}')
        key = []
        for x in cursor:
            key.append(x[0])
        cursor.executemany(f'DELETE FROM {TABLE_NAME} WHERE name = (%s)', key)
        db.commit()
        print(f'Deleted all data from {TABLE_NAME}')


data = DataBaseHandler()
# data.delete_all()

data.display_table()
