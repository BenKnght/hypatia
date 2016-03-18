import mysql.connector
from mysql.connector import errorcode

from DataSource import DataSource


class MySQL(DataSource):
    def __init__(self):
        DataSource.__init__(self)

    @staticmethod
    def insert(table, columns):
        """
        MySQL insert command
        Ref: https://dev.mysql.com/doc/connector-python/en/connector-python-example-cursor-transaction.html
        :param table: name of relational table
        :param columns: list of columns
        :return: SQL insert command string
        """
        values = ','.join(map(lambda x: '%({})s'.format(x), columns))
        return """
            INSERT INTO {}
            ({})
            VALUES ({})
        """.format(table, ','.join(columns), values)

    @staticmethod
    def get_connection():
        try:
            # TODO: Do not use root to connect
            # TODO: Have a secrets file and save these values
            connection = mysql.connector.connect(user='root', password='root', database='astronomy')
            return connection
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)