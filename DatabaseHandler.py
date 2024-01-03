# Importing modules
import threading
import pymysql
from pymysql.cursors import Cursor

# table
TABLE_NAME = "User"  # While changing do change even in 'get_db()'

# database and cursor
db: pymysql.connect = None
cursor: Cursor = None


def get_db():
    """Connects to the database"""
    global db, cursor
    try:
        db = pymysql.connect(
            host="localhost",
            user="Tester",  # 'GodGamer'
            passwd="Tester@2023",  # 'GodGamerData@2023'
            database="Chat",
        )
        cursor = db.cursor()
        cursor.execute(
            f"create table if not exists User(name VARCHAR(50) NOT NULL PRIMARY KEY, pass VARCHAR(50) NOT NULL)"
        )
        print(type(cursor))
    except Exception as e:
        print("Not able to login using 'tester' as user", e)
        try:
            db = pymysql.connect(host="localhost", user="root", passwd="root@123")
            cursor.execute("create database if not exists Chat")
            cursor.execute(
                f"create table if not exists User(name VARCHAR(50) NOT NULL PRIMARY KEY, pass VARCHAR(50) NOT NULL)"
            )
        except Exception as e:
            print("Not able to login using 'root' as user", e)


threading.Thread(target=get_db).start()


class DataBaseHandler:
    def __init__(self):
        if cursor is None:
            get_db()
        pass

    @staticmethod
    def adduser(username: str, password: str):
        """
        Adds the user to the database
        :param username: to be added to the database
        :param password: to be added to the database
        :return: (Boolean, Message: str) false if already present
        """
        if cursor is None:
            get_db()
        out = DataBaseHandler.check_user(username, password)
        if (
            not out[0] and out[1] != "Password is incorrect"
        ):  # check if the user is already added
            cursor.execute(
                f"INSERT INTO {TABLE_NAME} (name, pass) VALUES (%s,%s)",
                (username, password),
            )
            print(f"{username} added")
            db.commit()
            return True, "Signed up Successfully"
        else:  # display username is already present
            print(f"{username} already in use")
            return False, "Username already in use"

    @staticmethod
    def check_user(username: str, password: str):
        """
        Checks if the user is present and the password is correct
        :param username: to be checked
        :param password: to be checked
        :return: (Boolean, Message: str) false if not matching
        """
        if cursor is None:
            get_db()
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        for x in cursor:
            if x[0] == username:  # checking username
                if x[1] == password:  # checking password
                    return True, "All credentials correct"
                else:
                    return False, "Password is incorrect"
        return False, "No user found, please sign up"

    @staticmethod
    def delete_user(username: str):
        """Deleting user from database"""
        if cursor is None:
            get_db()
        cursor.execute(f"DELETE FROM {TABLE_NAME} where name = (%s)", (username,))
        print(f"{username} deleted")
        db.commit()

    @staticmethod
    def display_table():
        """Display the table"""
        if cursor is None:
            get_db()
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        for x in cursor:
            print(x)

    @staticmethod
    def delete_all():
        """Clear the table"""
        if cursor is None:
            get_db()
        cursor.execute(f"DELETE FROM {TABLE_NAME}")
        db.commit()
        print(f"Deleted all data from {TABLE_NAME}")


# data = DataBaseHandler()
# data.delete_all()

# data.display_table()
