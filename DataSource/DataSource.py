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

    @staticmethod
    def get_connection():
        raise NotImplementedError(DataSource.__message__("New Connection"))