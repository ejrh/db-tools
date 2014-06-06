from dbinterface import DatabaseInterface
from dbinterface import RootObject, DatabaseObject, SchemaObject, RelationObject, ColumnObject


class InformationSchemaInterface(DatabaseInterface):
    
    def __init__(self):
        pass

    def get_databases(self, root):
        sql = """SELECT catalog_name FROM information_schema.information_schema_catalog_name"""
        result = self.query(sql)
        return [DatabaseObject(r[0], self, root) for r in result]

    def get_schemas(self, database):
        sql = """SELECT schema_name FROM information_schema.schemata WHERE catalog_name = %(dbname)s"""
        dbname = database.name
        result = self.query(sql, locals())
        return [SchemaObject(r[0], self, database) for r in result]

    def get_relations(self, schema):
        sql = """SELECT table_name, table_type FROM information_schema.tables WHERE table_catalog = %(dbname)s AND table_schema = %(sname)s"""
        dbname = schema.parent.name
        sname = schema.name
        result = self.query(sql, locals())
        results = []
        for r in result:
            ro = RelationObject(r[0], self, schema)
            if r[1] == 'VIEW':
                ro.type = 'view'
            else:
                ro.type = 'table'
            results.append(ro)
        return results

    def get_columns(self, relation):
        sql = """SELECT column_name, udt_name, ordinal_position FROM information_schema.columns WHERE table_catalog = %(dbname)s AND table_schema = %(sname)s AND table_name = %(rname)s"""
        dbname = relation.parent.parent.name
        sname = relation.parent.name
        rname = relation.name
        result = self.query(sql, locals())
        results = []
        for r in result:
            co = ColumnObject(r[0], self, relation)
            co.type = r[1]
            co.num = r[2]
            results.append(co)
        return results
