class DatabaseInterface(object):
    def __init__(self):
        pass
    
    def get_root(self):
        return RootObject('Root', self)


class InterfaceObject(object):
    def __init__(self, name=None, db=None, parent=None):
        self.name = name
        self.db = db
        self.parent = parent
        self.children = {}
        self.populated = False
        if parent is not None:
            parent.children[name] = self

    def populate(self):
        self.children = {}
        if self.child_getter is not None:
            getter = getattr(self.db, self.child_getter)
            for c in getter(self):
                self.children[c.name] = c
        self.populated = True

    def get_child_names(self):
        names = self.children.keys()
        names.sort()
        return names


class RootObject(InterfaceObject):
    child_getter = 'get_databases'


class DatabaseObject(InterfaceObject):
    child_getter = 'get_schemas'

    def get_type_str(self):
        return 'Database'


class SchemaObject(InterfaceObject):
    child_getter = 'get_relations'

    def get_type_str(self):
        return 'Schema'


class RelationObject(InterfaceObject):
    child_getter = 'get_columns'

    def get_type_str(self):
        if self.type == 'table':
            return 'Table'
        else:
            return 'View'

    def get_child_names(self):
        values = self.children.values()
        values.sort(lambda a, b: a.num - b.num)
        return [c.name for c in values]


class ColumnObject(InterfaceObject):
    child_getter = None

    def __init__(self, name=None, db=None, parent=None):
        InterfaceObject.__init__(self, name, db, parent)
        self.populated = True
    
    def get_type_str(self):
        return self.type
