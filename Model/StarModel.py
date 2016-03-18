from DataSource.MySQLDataSource import MySQL
from Model import Model


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
        :param connection: open connection to database
        :param hip: [required] unique id for the star. If not set now, has to be set later
        :param attr_values: all other attributes of the star as a dictionary. refer defaults for available attributes
        :return: instance
        """
        Model.__init__(self)
        self.columns = Star.DEFAULTS
        self.columns['hip'] = hip
        if attr_values:
            self.columns.update(attr_values)
        self.columns['created_at'] = self.created_at
        self.columns['updated_at'] = self.updated_at

    def set(self, attribute, value):
        if attribute not in self.columns:
            raise ValueError("Unknown column, %s" % (attribute,))
        self.columns[attribute] = value

    def save(self, connection):
        """
        saves the changes to in-memory object to disk
        :param connection: open connection to DB. Assumes auto-commit is OFF
        :return: True if success, None if failed
        """
        super(Star, self).save()
        add_star = MySQL.insert("star", self.columns.keys())
        c = connection.cursor()
        c.execute(add_star, self.columns)
        connection.commit()
        c.close()