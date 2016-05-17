from Model import Model
from DataSource.MySQLDataSource import MySQL


class Planet(Model):
    """
    Planet Model class
    """
    TABLE = 'planet'
    DEFAULTS = {
        'name': None,
        'hip': None,
        'm_p': None,
        'p': None,
        'e': None,
        'a': None
    }

    def __init__(self, name, hip, m_p, p, e, a):
        """
        initializes a composition object
        Each argument is a column
        :return: instance
        """
        super(Planet, self).__init__()
        self.columns.update(self.DEFAULTS)
        self.columns['name'] = name
        self.columns['hip'] = hip
        self.columns['m_p'] = m_p
        self.columns['p'] = p
        self.columns['e'] = e
        self.columns['a'] = a

    def find(self, connection, only_one=True):
        """
        Finds in the database for this planet
        :param connection: open connection
        :param only_one: if True, only the first record returned by DB is returned, else all are returned
        :return: record(s) if found, else None
        """
        find_planet_sql = MySQL.select(self.TABLE, ['hip', 'name'], ['=', '='], ['AND'])
        return super(Planet, self).find(find_planet_sql,
                                        {'hip': self.columns['hip'], 'name': self.columns['name']},
                                        connection, only_one)

    def upsert(self, connection):
        """
        saves or updates
        :param connection: open connection
        :return: record ID
        """
        inserted, rid = super(Planet, self).upsert(connection)
        if not inserted:
            rid = (
                self.columns['hip'],
                self.columns['name'])  # TODO: check if this is the way DB returns on c.lastrowid call
        return rid

    def update(self, connection):
        self.columns.pop('created_at', None)  # So that original timestamp is not overwritten with current one
        update_planet_sql = MySQL.update(self.TABLE, self.columns.keys(), ['hip', 'name'], ['=', '='], ['AND'])
        return super(Planet, self).update(update_planet_sql, connection)
