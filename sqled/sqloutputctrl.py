import wx.grid

class SQLOutputCtrl(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        
        self.EnableEditing(False)
        self.CreateGrid(1, 1)

    def populate(self, description, result):
        if self.GetNumberRows() > 0:
            self.DeleteRows(0, self.GetNumberRows())
        if self.GetNumberCols() > 0:
            self.DeleteCols(0, self.GetNumberCols())

        self.InsertCols(0, len(description))
        i = 0
        for f in description:
            self.SetColLabelValue(i, f[0]);
            i += 1
        
        self.InsertRows(0, len(result))
        i = 0
        for r in result:
            for j in range(0, len(r)):
                self.SetCellValue(i, j, str(r[j]))
            i += 1

    def OnCopy(self, event):
        print 'copy'
