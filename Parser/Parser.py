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