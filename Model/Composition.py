from Model import Model


class Composition(Model):
    """
    Composition Model class
    """
    TABLE = 'composition'
    DEFAULTS = {
        'hip': None,
        'cid': None,
        'element': None,
        'value': None
    }

    def __init__(self, hip, cid, element, value):
        """
        initializes a composition object
        :param hip: [required] unique id for the star. If not set now, has to be set later
        :param cid: [required] unique id for the star. If not set now, has to be set later
        :param element: [required] unique id for the star. If not set now, has to be set later
        :param value: [required] unique id for the star. If not set now, has to be set later
        :return: instance
        """
        Model.__init__(self)
        self.columns.update(self.DEFAULTS)
        self.columns['hip'] = hip
        self.columns['cid'] = cid
        self.columns['element'] = element
        self.columns['value'] = value
