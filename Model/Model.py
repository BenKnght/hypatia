import datetime
from DataSource.MySQLDataSource import MySQL


class Model(object):
    TABLE = None  # Name of the table in database
    DEFAULTS = None  # Default column values. To be set my concrete classes

    def __init__(self):
        self.columns = {
            'created_at': None,
            'updated_at': None
        }

    def set(self, attribute, value):
        if attribute not in self.columns:
            raise ValueError("Unknown column, %s" % (attribute,))
        self.columns[attribute] = value

    def save(self, connection):
        """
        saves the changes to in-memory object to disk
        :param connection: open connection to DB. Assumes auto-commit is OFF
        :return: ID of the newly inserted entity
        """
        self.columns['created_at'] = datetime.datetime.today()
        self.columns['updated_at'] = self.columns['created_at']

        add_entity = MySQL.insert(self.TABLE, self.columns.keys())
        c = connection.cursor()
        c.execute(add_entity, self.columns)
        connection.commit()
        c.close()
        return c.lastrowid

    def update(self):
        self.columns['updated_at'] = datetime.datetime.today()
