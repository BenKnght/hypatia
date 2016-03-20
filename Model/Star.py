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
        :param hip: [required] unique id for the star. If not set now, has to be set later
        :param attr_values: all other attributes of the star as a dictionary. refer defaults for available attributes
        :return: instance
        """
        Model.__init__(self)
        self.columns.update(self.DEFAULTS)
        self.columns['hip'] = hip
        if attr_values:
            self.columns.update(attr_values)
