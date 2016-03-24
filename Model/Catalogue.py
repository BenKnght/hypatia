from Model import Model
from DataSource.MySQLDataSource import MySQL


class Catalogue(Model):
    """
    Catalogue Model class
    """
    TABLE = 'catalogue'
    DEFAULTS = {
        'id': None,
        'author_year': None,
    }

    def __init__(self, author_year):
        """
        initializes a catalogue object
        :param author: [required] Author of the catalogue, paper
        :return: instance
        """
        super(Catalogue, self).__init__()
        self.columns.update(self.DEFAULTS)
        self.columns['author_year'] = author_year

    def find(self, connection, only_one=True):
        """
        Finds in the database for a catalogue by author and year
        :param connection: open connection
        :param only_one: if True, only the first record returned by DB is returned, else all are returned
        :return: record(s) if found, else None
        """
        find_catalogue = MySQL.select(self.TABLE, ['author_year'],
                                      ['='], [])
        return super(Catalogue, self).find(find_catalogue,
                                           [self.columns['author_year'].strip()], connection, only_one)

    def upsert(self, connection):
        """
        saves or updates
        :param connection: open connection
        :return: record ID
        """
        inserted, rid = super(Catalogue, self).upsert(connection)
        if not inserted:
            # assumption: first column returned from select * is always `id` which is the primary key for this table
            self.columns['id'] = rid[0]
            rid = rid[0]  # set rid to be record id instead of entire record
        return rid
