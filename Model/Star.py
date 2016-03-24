from Model import Model
from DataSource.MySQLDataSource import MySQL


class Star(Model):
    """
    Star Model class
    """
    TABLE = 'star'
    DEFAULTS = {
        'hip': None,
        'hd': None,
        'bd': None,
        'hr': None,
        'spec': None,
        'vmag': None,
        'bv': None,
        'dist': None,
        'rascension': None,
        'declination': None,
        'position': None,
        'disk': None,
        'uvw': None
    }

    def __init__(self, hip, **attr_values):
        """
        initializes a star object
        :param hip: [required] unique id for the star. If not set now, has to be set later
        :param attr_values: all other attributes of the star as a dictionary. refer defaults for available attributes
        :return: instance
        """
        super(Star, self).__init__()
        self.columns.update(self.DEFAULTS)
        self.columns['hip'] = hip
        if attr_values:
            self.columns.update(attr_values)

    def find(self, connection, only_one=True):
        """
        Finds in the database for a star by HIP
        :param connection: open connection
        :param only_one: if True, only the first record returned by DB is returned, else all are returned
        :return: record(s) if found, else None
        """
        find_star = MySQL.select(self.TABLE, ['hip'], ['='])
        return super(Star, self).find(find_star, [self.columns['hip']], connection, only_one)

    def upsert(self, connection):
        """
        saves or updates
        :param connection: open connection
        :return: record ID
        """
        inserted, rid = super(Star, self).upsert(connection)
        if not inserted:
            rid = self.columns['hip']
        return rid
