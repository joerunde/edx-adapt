"""Storage module that implements StorageInterface using an sqlitedict backend. (Should be) thread safe """


import interface
from sqlitedict import SqliteDict


class SqliteStorage(interface.StorageInterface):

    def __init__(self, db_path):
        super(SqliteStorage, self).__init__()
        #self.db = TinyDB(db_path)
        self.path = db_path
        #make a "tables" table
        self.table_names = SqliteDict(self.path, tablename='__TABLES__', autocommit=True)
        self.tables = {}
        if('tables' in self.table_names):
            for name in self.table_names['tables']:
                self.tables[name] = SqliteDict(self.path, tablename=name, autocommit=True)
        else:
            self.table_names['tables'] = []

    def create_table(self, table_name):
        self._assert_no_table(table_name)
        l = self.table_names['tables']
        l.append(table_name)
        self.table_names['tables'] = l
        table = SqliteDict(self.path, tablename=table_name, autocommit=True)
        self.tables[table_name] = table

        print self.table_names['tables']

    def get_tables(self):
        #just return table names, not actual tables
        return self.table_names['tables']

    def get(self, table_name, key):
        self._assert_table(table_name)
        table = self.tables[table_name]
        if key not in table:
            raise interface.DataException("Key {} not found in table".format(key))
        return table[key]

    def set(self, table_name, key, val):
        self._assert_table(table_name)
        table = self.tables[table_name]
        table[key] = val

    def append(self, table_name, list_key, val):
        self._assert_table(table_name)
        table = self.tables[table_name]
        if list_key not in table:
            raise interface.DataException("List: {0} not in table: {1}".format(list_key, table_name))
        l = table[list_key]
        #TODO: check if l is a list maybe
        if val in l:
            raise interface.DataException("Value: {0} already exists in list: {1}".format(val, list_key))
        l.append(val)
        table[list_key] = l

    def remove(self, table_name, list_key, val):
        #TODO: do
        raise NotImplementedError("Storage module must implement this")

    def _assert_no_table(self, table_name):
        if table_name in self.table_names['tables']:
            raise interface.DataException("Table already exists: {}".format(table_name))

    def _assert_table(self, table_name):
        if table_name not in self.table_names['tables']:
            print self.table_names['tables']
            raise interface.DataException("Table does not exist: {}".format(table_name))