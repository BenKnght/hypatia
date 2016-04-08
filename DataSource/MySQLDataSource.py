import mysql.connector
from mysql.connector import errorcode
import os

from DataSource import DataSource
from Config import logger


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
    def update(table, columns_to_update, condition_columns, condition_operators, condition_types=[]):
        """
        MySQL update command
        Ref: https://dev.mysql.com/doc/connector-python/en/connector-python-example-cursor-transaction.html
        :param table: name of the relational table
        :param columns_to_update: list of columns to update
        :param condition_columns: list of columns in-order to appear in the WHERE clause
        :param condition_operators: list of operators (=, <=, >=, <, >, <>) joining condition columns and values
        :param condition_types: list of combiners joining conditions (AND, OR)
        :return: update SQL string
        """
        values = map(lambda x: '{}=%({})s'.format(x, x), columns_to_update)
        conditions_and_types = MySQL._create_conditions(condition_columns, condition_types, condition_operators)
        return """
            UPDATE {}
            SET {}
            WHERE {}
        """.format(table, ','.join(values), ' '.join(conditions_and_types))

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
        conditions_and_types = MySQL._create_conditions(columns, condition_types, operators)
        return """
        SELECT *
        FROM {}
        WHERE {}
        """.format(table, ' '.join(conditions_and_types))

    @staticmethod
    def _create_conditions(columns, condition_types, operators):
        if len(columns) is not len(operators) is not len(condition_types) - 1:
            raise ValueError("Number of conditions, values and conditions do not match")
        conditions = ["{} {} %({})s".format(columns[i], op, columns[i]) for i, op in enumerate(operators)]
        if len(condition_types) > 0:
            conditions_and_types = [None] * (2 * len(conditions) - 1)
            conditions_and_types[::2] = conditions
            conditions_and_types[1::2] = condition_types
        else:
            conditions_and_types = conditions
        return conditions_and_types

    @staticmethod
    def get_connection(database='astronomy'):
        """
        Returns an open Database connection
        Set db_username, db_password and db_name environment variables if defaults are not good
        :param database: database name to connect to
        :return: open MySQL connection
        """
        try:
            # TODO: Do not use root to connect by default
            host = os.environ['DB_HOSTNAME'] if 'DB_HOSTNAME' in os.environ else '127.0.0.1'
            user = os.environ['DB_USERNAME'] if 'DB_USERNAME' in os.environ else 'root'
            password = os.environ['DB_PASSWORD'] if 'DB_PASSWORD' in os.environ else 'root'
            database = os.environ['DB_NAME'] if 'DB_NAME' in os.environ else database
            connection = mysql.connector.connect(user=user, password=password, database=database, host=host)
            return connection
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logger.warning("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logger.warning("Database does not exist")
            else:
                logger.warning(err)
