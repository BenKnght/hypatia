import time


class Model(object):
    def __init__(self):
        self.created_at = None
        self.updated_at = None

    def save(self):
        self.created_at = time.time()
        self.created_at = self.created_at

    def update(self):
        self.updated_at = time.time()