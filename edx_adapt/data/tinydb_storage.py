"""Storage module that implements StorageInterface using a tinydb backend. Not entirely thread safe """


import interface
from tinydb import TinyDB, Query


class TinydbStorage(interface.StorageInterface):

    def __init__(self, db_path):
        super(TinydbStorage, self).__init__()
        self.db = TinyDB(db_path)

    def create_table(self, table_name):
        self._assert_no_table(table_name)
        table = self.db.table(table_name)
        table.insert({'table_exists': True})

    def get_tables(self):
        return self.db.tables()

    def get(self, table_name, key):
        self._assert_table(table_name)
        table = self.db.table(table_name)
        element = Query()
        result = table.search(element.key == key)
        if len(result) == 0:
            raise interface.DataException("Key {} not found in table".format(key))
        return result[0]['val']

    def set(self, table_name, key, val):
        self._assert_table(table_name)
        table = self.db.table(table_name)
        element = Query()
        table.remove(element.key == key)
        table.insert({'key': key, 'val': val})

    def append(self, table_name, list_key, val):
        self._assert_table(table_name)
        table = self.db.table(table_name)
        l = self.get(table_name, list_key)
        #TODO: check if l is a list maybe
        if val in l:
            raise interface.DataException("Value: {0} already exists in list: {1}".format(val, list_key))
        l.append(val)
        element = Query()
        table.update({'val': l}, element.key == list_key)

    def remove(self, table_name, list_key, val):
        #TODO: do
        raise NotImplementedError("Storage module must implement this")

    def _assert_no_table(self, table_name):
        table = self.db.table(table_name)
        if len(table) > 0:
            raise interface.DataException("Table already exists: {}".format(table_name))

    def _assert_table(self, table_name):
        table = self.db.table(table_name)
        if len(table) == 0:
            raise interface.DataException("Table does not exist: {}".format(table_name))