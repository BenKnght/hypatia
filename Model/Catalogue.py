from Model import Model


class Catalogue(Model):
    """
    Catalogue Model class
    """
    TABLE = 'catalogue'
    DEFAULTS = {
        'id': None,
        'author': None,
        'year': None,
    }

    def __init__(self, author, year):
        """
        initializes a catalogue object
        :param author: [required] Author of the catalogue, paper
        :param year: [required] Year(s) as a string published
        :return: instance
        """
        Model.__init__(self)
        self.columns.update(self.DEFAULTS)
        self.columns['author'] = author
        self.columns['year'] = year
