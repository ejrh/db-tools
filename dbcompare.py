import sys
import re
from optparse import OptionParser

query_re = re.compile('SELECT\s.*', re.IGNORECASE)

def connect(username, password, connstr):
    parts = connstr.split(':')
    if parts[0] == 'oracle':
        # oracle:HOST:1521:SID
        host = parts[1]
        port = int(parts[2])
        sid = parts[3]
        import cx_Oracle
        try:
            conn = cx_Oracle.Connection(username, password, dsn=cx_Oracle.makedsn(host, port, sid))
        except cx_Oracle.DatabaseError:
            conn = cx_Oracle.Connection(username, password, dsn=cx_Oracle.makedsn(host, port, service_name=sid))
    else:
        raise NotImplementedError("Unknown database type '%s'" % parts[0])
    return conn

def get_tables(conn):
    cursor = connections[0].cursor()
    cursor.execute("SELECT DISTINCT table_name FROM user_tab_cols ORDER BY table_name")
    results = []
    for r in cursor.fetchall():
        results.append(r[0])
    cursor.close()
    return results

def get_columns(conn, table_name):
    sql = """SELECT DISTINCT column_name, column_id FROM user_tab_cols WHERE table_name = '%s' ORDER BY column_id""" % table_name
    cursor = conn.cursor()
    cursor.execute(sql)
    results = []
    for r in cursor.fetchall():
        results.append(r[0])
    cursor.close()
    if len(results) == 0:
        raise Exception("Couldn't find any columns for table '%s'" % table_name)
    return results

def get_pk_columns(conn, table_name):
    sql = """SELECT cols.column_name, cols.position
    FROM all_constraints cons JOIN all_cons_columns cols ON (cons.constraint_name = cols.constraint_name AND cons.owner = cols.owner)
    WHERE cols.table_name = '%s'
    AND cons.constraint_type = 'P'
    ORDER BY cols.position"""
    cursor = conn.cursor()
    cursor.execute(sql % table_name)
    results = []
    for r in cursor.fetchall():
        results.append(r[0])
    cursor.close()
    if len(results) == 0:
        raise Exception("Couldn't find any primary key columns for table '%s'" % table_name)
    return results

def get_table_sql(conn, table_name):
    cols = get_columns(conn, table_name)
    col_str = ','.join(cols)
    pk_cols = get_pk_columns(conn, table_name)
    order_by_str = ','.join(pk_cols)
    sql = "SELECT %s FROM %s ORDER BY %s" % (col_str, table_name, order_by_str)
    return sql

def open_query(conn, sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor

def get_column_row(cursor):
    return [x[0] for x in cursor.description]

def get_diff_stream(conn, table_or_query):
    if query_re.match(table_or_query):
        sql = table_or_query
    else:
        sql = get_table_sql(conn, table_or_query)
    
    cursor = open_query(conn, sql)
    
    yield get_column_row(cursor)
    
    for row in cursor.fetchall():
        yield row
    
    cursor.close()

def compare_databases(options):
    connections = []
    for i in range(2):
        conn = connect(options.username[i], options.password[i], options.connstr[i])
        connections.append(conn)
    
    diff_stream = []
    for i in range(2):
        diff_stream.append(get_diff_stream(connections[i], options.table_name[i]))
    
    row0 = None
    row1 = None
    while True:
        if row0 is None:
            try:
                row0 = diff_stream[0].next()
            except StopIteration:
                row0 = None
        if row1 is None:
            try:
                row1 = diff_stream[1].next()
            except StopIteration:
                row1 = None
        
        if row0 is None and row1 is None:
            break
        
        if row1 is None or (row0 is not None and row0 < row1):
            print '-%s' % str(row0)
            row0 = None
        elif row0 is None or (row1 is not None and row0 > row1):
            print '+%s' % str(row1)
            row1 = None
        elif row0 == row1:
            if options.all:
                print ' %s' % str(row0)
            row0 = None
            row1 = None
    
    for i in range(2):
        connections[i].close()

def main():
    usage = """usage: %prog -u USERNAME1 [-u USERNAME2] -p PASSWORD1 [-p PASSWORD2] -c CONNECTION1 [-c CONNECTION2] {-t TABLE1|-q QUERY1} [-t TABLE2|-q QUERY2] [-a]"""
    desc = """Compare two tables or queries"""
    parser = OptionParser(usage=usage, description=desc)
    parser.add_option("-u", "--username", metavar="USERNAME",
                      action="append", dest="username", default=[],
                      help="Database user name")
    parser.add_option("-p", "--password", metavar="PASSWORD",
                      action="append", dest="password", default=[],
                      help="Database password")
    parser.add_option("-c", "--connstr", metavar="CONNECTION",
                      action="append", dest="connstr", default=[],
                      help="Database connection string")
    parser.add_option("-t", "--table", metavar="TABLE",
                      action="append", dest="table_name", default=[],
                      help="Table to compare")
    parser.add_option("-q", "--query", metavar="QUERY",
                      action="append", dest="query_sql", default=[],
                      help="Query to compare")
    parser.add_option("-a", "--all",
                      action="store_true", dest="all", default=False,
                      help="Output all rows")

    options, args = parser.parse_args()
    if len(args) > 0:
        parser.error("Unexpected additional arguments: %s" % args)

    for opt in parser.option_list:
        if opt.dest not in ['username', 'password', 'connstr', 'table_name', 'query_sql']:
            continue
        dest = getattr(options, opt.dest)
        if len(dest) > 2:
            parser.error('Too many values for %s' % opt._long_opts[0])
        if len(dest) == 1:
            dest.append(dest[0])
    
    if len(options.table_name) == 0 and len(options.query_sql) == 0:
        parser.error('Need one of --table or --query')
    
    compare_databases(options)

if __name__ == '__main__':
    main()
