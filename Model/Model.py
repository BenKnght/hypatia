import datetime, json
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
        connection.commit()  # TODO: Decide if this is OK as rollbacks can be difficult
        c.close()
        return c.lastrowid

    def upsert(self, connection):
        """
        Check if current instance exists in DB, if yes, update it, else add it
        :param connection: open connection
        :return: [True, rid] if inserted else [False, entire record]
        """
        # Check if this entity exists using default find method
        record = self.find(connection)
        if not record:
            return [True, self.save(connection)]
        else:
            self.update(connection)
            return [False, record]

    def find(self, sql_template, values, connection, only_one=True):
        """
        Finds entity using the given SQL
        :param sql_template: sql to execute
        :param values: dictionary of values with key as the column name and value as whatever value is required to find
        :param connection: open connection
        :param only_one: if set, only one record is returned if found
        :return: instance(s) if found, else None
        """
        c = connection.cursor()
        c.execute(sql_template, values)
        if only_one:
            records = c.fetchone()
        else:
            records = c.fetchall()
        c.close()
        return records

    def update(self, sql_template, connection):
        """
        update entity to data store
        placeholders in the SQL template are safely replaced by column values of the Model
        :param sql_template: SQL template string with placeholders for values
        :param connection: open connection
        :return: True always
        """
        self.columns['updated_at'] = datetime.datetime.today()
        c = connection.cursor()
        c.execute(sql_template, self.columns)
        connection.commit()  # TODO: Decide if this is OK as rollbacks can be difficult
        c.close()
        return True

    def __str__(self):
        return json.dumps(self.columns)
