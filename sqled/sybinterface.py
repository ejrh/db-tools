import dbutil
from dbinterface import DatabaseInterface
from dbinterface import RootObject, DatabaseObject, SchemaObject, RelationObject, ColumnObject


class SybaseInterface(DatabaseInterface):
    
    def __init__(self, params):
        DatabaseInterface.__init__(self)
        self.dbname = params['database']
        self.connopts = dbutil.ConnectOptions(**params)
        self.conn = self.connopts.MakeConnection()
        self.cursor = self.conn.cursor()

    def get_databases(self, root):
        return [DatabaseObject(self.dbname, self, root)]
        #sql = """sp_helpdb"""
        #result = self.query(sql)
        #return [DatabaseObject(r[0].strip(), self, root) for r in result]

    def get_schemas(self, database):
        if database.name != self.dbname:
            return []
        return [SchemaObject(r, self, database) for r in ['dbo']]

    def get_relations(self, schema):
        sql = """SELECT name, type FROM sysobjects"""
        result = self.query(sql)
        results = []
        for r in result:
            if r[1].strip() in ['U', 'V']:
                ro = RelationObject(r[0].strip(), self, schema)
                if r[1].strip() == 'V':
                    ro.type = 'view'
                else:
                    ro.type = 'table'
                results.append(ro)
        return results

    def get_columns(self, relation):
        sql = """SELECT c.name, t.name, c.colid FROM sysobjects AS o JOIN syscolumns AS c ON o.id = c.id JOIN systypes AS t ON c.usertype = t.usertype WHERE o.name = '%s'""" % relation.name
        result = self.query(sql)
        results = []
        for r in result:
            co = ColumnObject(r[0].strip(), self, relation)
            co.type = r[1].strip()
            co.num = r[2]
            results.append(co)
        return results

    def query(self, sql, values={}):
        self.cursor.execute(sql, values)
        return self.cursor.fetchall()
