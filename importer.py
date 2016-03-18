import mysql.connector
from mysql.connector import errorcode
import time
import re


class Model(object):
    def __init__(self):
        self.created_at = None
        self.updated_at = None

    def save(self):
        self.created_at = time.time()
        self.created_at = self.created_at

    def update(self):
        self.updated_at = time.time()


class DataSource(object):
    def __init__(self):
        pass

    @staticmethod
    def __message__(method):
        return "%s function not implemented" % (method,)

    @staticmethod
    def insert():
        raise NotImplementedError(DataSource.__message__("Insert"))

    @staticmethod
    def update():
        raise NotImplementedError(DataSource.__message__("Update"))

    @staticmethod
    def select():
        raise NotImplementedError(DataSource.__message__("Select"))

    @staticmethod
    def delete():
        raise NotImplementedError(DataSource.__message__("Delete"))


class Parser(object):
    def __init__(self, filepath):
        self.path = filepath

    def __enter__(self):
        self.f = open(self.path, 'r')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.f.close()

    def next(self):
        """
        An iterator for receiving entities
        :return: the next entity if present else None
        """
        raise NotImplementedError("next method not implemented; cannot get next entity")


class HypatiaParser(Parser):
    def __init__(self, filepath):
        Parser.__init__(self, filepath)

    # Note: Keys should be in lower case
    hypatia_column_map = {
        'hip': 'hip',
        'hd': 'hd',
        'bd': 'bd',
        'hr': 'hr',
        'spec type': 'spec',
        'vmag': 'vmag',
        'b-v': 'bv',
        'dist (pc)': 'dist',
        'ra/dec': ['rascension', 'declination'],
        'position': 'position',
        'disk component': 'disk',
        'uvw': 'uvw'
    }

    def next(self):
        """
        Fetches the next star from Custom Hypatia format
        :return: Star instance
        """
        with open(self.path) as f:
            raw_stars = f.read().split("\n\n")  # Assumption: Each star is separated by ONE blank line
            for raw_star in raw_stars:
                try:
                    s = Star(None)
                    raw_star_attrs = raw_star.split("\n")  # Assumption: Each attribute of the star is on its own line
                    for raw_attr in raw_star_attrs:
                        # Split attributes and values of the star. They are separated by a '=' or ':'
                        # Once split, the last entity is value and the last but one is the key
                        attr_value = re.split(r'=|:', raw_attr)
                        if len(attr_value) > 1:
                            key = attr_value[-2].lower().strip()
                            value = attr_value[-1].strip()
                            if key in self.hypatia_column_map:
                                if key == 'ra/dec':
                                    m = re.match(r'\((.+),(.+)\)', value)
                                    ra, dec = m.groups()
                                    s.set('rascension', float(ra.strip()))
                                    s.set('declination', float(dec.strip()))
                                else:
                                    s.set(self.hypatia_column_map[key], value)
                        else:
                            # composition attributes of star
                            pass
                    yield s
                except:
                    # TODO: Log that a star has been skipped
                    raise
                    pass


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


def main():
    c = get_connection()
    p = HypatiaParser('/Volumes/350GB/Projects/RA/Assets/test_inp.txt')
    if c:
        for star in p.next():
            try:
                star.save(c)
            except:
                # TODO: Log failed save
                pass
        c.close()


if __name__ == '__main__':
    main()
