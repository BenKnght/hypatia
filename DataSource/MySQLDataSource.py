import mysql.connector
from mysql.connector import errorcode
import logging

from DataSource import DataSource


class MySQL(DataSource):
    def __init__(self):
        super(MySQL, self).__init__()

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
    def select(table, columns, operators, condition_types=[]):
        """
        MySQL select command
        :param table: source table on which SELECT has to be executed
        :param columns: list of columns in-order participating in WHERE condition
        :param operators: list of operators joining the columns and values
        :param condition_types: list of 'AND' or 'OR' terms
        :return: Returns entire tuples which match the selection criteria
        """
        if len(columns) is not len(operators) is not len(condition_types) - 1:
            raise ValueError("Number of conditions, values and conditions do not match")

        conditions = ["{} {} %s".format(columns[i], op) for i, op in enumerate(operators)]
        if len(condition_types) > 0:
            conditions_and_types = [None] * (2 * len(conditions) - 1)
            conditions_and_types[::2] = conditions
            conditions_and_types[1::2] = condition_types
        else:
            conditions_and_types = conditions
        return """
        SELECT *
        FROM {}
        WHERE {}
        """.format(table, ' '.join(conditions_and_types))

    @staticmethod
    def get_connection(database='astronomy'):
        try:
            # TODO: Do not use root to connect
            # TODO: Have a secrets file and save these values
            connection = mysql.connector.connect(user='root', password='root', database=database)
            return connection
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.warning("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.warning("Database does not exist")
            else:
                logging.warning(err)
