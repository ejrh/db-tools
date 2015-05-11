import wx

from dbinterface.postgres import PGInterface

from sqltreectrl import SQLTreeCtrl
from sqleditctrl import SQLEditCtrl
from sqloutputctrl import SQLOutputCtrl


class MainFrame(wx.Frame):
    def __init__(self, parent=None, ID=-1, pos=wx.DefaultPosition, size=wx.Size(800, 600), style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, ID, 'SQL Editor', pos, size, style)
        
        self.CreateStatusBar()
        
        self.vsplitter = wx.SplitterWindow(self)
        self.hsplitter = wx.SplitterWindow(self.vsplitter)
        self.tree = SQLTreeCtrl(self.vsplitter)
        self.tc = SQLEditCtrl(self.hsplitter)
        self.output = SQLOutputCtrl(self.hsplitter)
        self.hsplitter.SetMinimumPaneSize(100)
        self.vsplitter.SetMinimumPaneSize(100)
        self.hsplitter.SplitHorizontally(self.tc, self.output, 500)
        self.vsplitter.SplitVertically(self.tree, self.hsplitter, 250)
        self.hsplitter.SetSashPosition(500)
        self.tc.SetFocus()
        
        self.BuildMenuBar()
        
        self.finddlg = None
        self.finddata = wx.FindReplaceData()
        self.finddata.SetFlags(wx.FR_DOWN)
        
        params = {'dbname': 'svnindex', 'host': 'localhost', 'user': 'localuser', 'password': 'localuser'}
        conn = PGInterface(params)
        conn.name = "svnindex on localhost"
        
        self.tree.populate([conn])

    def BuildMenuBar(self):
        self.menubar = wx.MenuBar()
        
        file_menu = wx.Menu()
        exit_item = wx.MenuItem(file_menu, -1, 'E&xit\tAlt-F4', 'Exit the SQL Editor')
        file_menu.AppendItem(exit_item)
        self.menubar.Append(file_menu, '&File')
        
        self.Bind(wx.EVT_MENU, self.OnFileExit, exit_item)
        
        edit_menu = wx.Menu()
        copy_item = wx.MenuItem(edit_menu, -1, '&Copy\tCtrl-C', 'Copy the current selection')
        edit_menu.AppendItem(copy_item)
        find_item = wx.MenuItem(edit_menu, -1, '&Find\tCtrl-F', 'Search for text in current editor window')
        edit_menu.AppendItem(find_item)
        find_next_item = wx.MenuItem(edit_menu, -1, 'Find &Next\tF3', 'Search for next occurrence of text')
        edit_menu.AppendItem(find_next_item)
        self.menubar.Append(edit_menu, '&Edit')
        
        self.Bind(wx.EVT_MENU, self.OnEditCopy)
        self.Bind(wx.EVT_MENU, self.OnEditFind, find_item)
        self.Bind(wx.EVT_MENU, self.OnEditFindNext, find_next_item)
        self.Bind(wx.EVT_FIND, self.OnFind)
        self.Bind(wx.EVT_FIND_NEXT, self.OnFind)
        self.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)
        
        command_menu = wx.Menu()
        run_item = wx.MenuItem(edit_menu, -1, '&Run\tF5', 'Run the currently selected SQL')
        command_menu.AppendItem(run_item)
        self.menubar.Append(command_menu, '&Command')
        
        self.Bind(wx.EVT_MENU, self.OnCommandRun, run_item)
        
        help_menu = wx.Menu()
        about_item = wx.MenuItem(file_menu, -1, '&About', 'Show program version information')
        help_menu.AppendItem(about_item)
        self.menubar.Append(help_menu, '&Help')
        
        self.Bind(wx.EVT_MENU, self.OnHelpAbout, about_item)
        
        self.SetMenuBar(self.menubar)

    def OnFileExit(self, event):
        self.Close()

    def OnEditCopy(self, event):
        if self.tc.HasFocus():
            self.tc.OnCopy(self, event)
        elif self.output.HasFocus():
            self.output.OnCopy(self, event)

    def OnEditFind(self, event):
        if self.finddlg is not None:
            return
        
        self.finddlg = wx.FindReplaceDialog(self, self.finddata, "Find",
                        wx.FR_NOMATCHCASE | wx.FR_NOWHOLEWORD)
        self.finddlg.Show(True)

    def OnEditFindNext(self, event):
        if self.finddata.GetFindString():
            self.OnFind(event)
        else:
            self.OnEditFind(event)
    
    def OnFind(self, event):
        editor = self.tc
        end = editor.GetLastPosition()
        textstring = editor.GetRange(0, end).lower()
        findstring = self.finddata.GetFindString().lower()
        backward = not (self.finddata.GetFlags() & wx.FR_DOWN)
        if backward:
            start = editor.GetSelection()[0]
            loc = textstring.rfind(findstring, 0, start)
        else:
            start = editor.GetSelection()[1]
            loc = textstring.find(findstring, start)
        if loc == -1 and start != 0:
            # string not found, start at beginning
            if backward:
                start = end
                loc = textstring.rfind(findstring, 0, start)
            else:
                start = 0
                loc = textstring.find(findstring, start)
        if loc == -1:
            dlg = wx.MessageDialog(self, 'Find String Not Found',
                          'Find String Not Found in Demo File',
                          wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        #if self.finddlg:
        #    if loc == -1:
        #        self.finddlg.SetFocus()
        #        return
        #    else:
        #        self.finddlg.Destroy()
        #        self.finddlg = None
        editor.ShowPosition(loc)
        editor.SetSelection(loc, loc + len(findstring))

    def OnFindClose(self, event):
        event.GetDialog().Destroy()
        self.finddlg = None
    
    def OnCommandRun(self, event):
        sql = self.tc.GetSelectedText()
        if sql == '':
            sql = self.tc.GetText()
        result = self.db.query(sql)
        self.output.populate(self.db.cursor.description, result)

    def OnHelpAbout(self, event):
        info = wx.AboutDialogInfo()
        info.SetName('SQL Editor')
        info.SetVersion(VERSION)
        info.AddDeveloper('Edmund Horner')
        wx.AboutBox(info)
