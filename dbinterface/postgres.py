import psycopg2
from isinterface import InformationSchemaInterface

class PGInterface(InformationSchemaInterface):
    
    def __init__(self, params):
        InformationSchemaInterface.__init__(self)
        self.conn = psycopg2.connect("dbname='%(dbname)s' user='%(user)s' host='%(host)s' password='%(password)s'" % params)
        self.cursor = self.conn.cursor()

    def query(self, sql, values={}):
        self.cursor.execute(sql, values)
        return self.cursor.fetchall()
