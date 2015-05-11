import wx
import wx.gizmos

class SQLTreeCtrl(wx.gizmos.TreeListCtrl):
    def __init__(self, parent):
        wx.gizmos.TreeListCtrl.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE)

        self.AddColumn("Object")
        self.AddColumn("Type")
        
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded)
        
    def populate(self, conns):
        self.root = self.AddRoot("Connections")
        for conn in conns:
            conn_item = self.AppendItem(self.root, conn.name)
            self.SetPyData(conn_item, conn.get_root())
            fake_item = self.AppendItem(conn_item, '*fake*')
            #self.populate_item(self.root)

    def populate_item(self, item):
        obj = self.GetPyData(item)
        if obj is None or obj.populated:
            return
        obj.populate()
        for childname in obj.get_child_names():
            child = obj.children[childname]
            childitem = self.AppendItem(item, child.name)
            self.SetPyData(childitem, child)
            self.SetItemText(childitem, child.get_type_str(), 1)
            if not child.populated:
                fakeitem = self.AppendItem(childitem, '*fake*')
        fakeitem = self.GetFirstChild(item)[0]
        if self.GetItemText(fakeitem) == '*fake*':
            self.Delete(fakeitem)

    def OnItemExpanded(self, event):
        item = event.GetItem()
        if not item:
            return
        self.populate_item(item)
