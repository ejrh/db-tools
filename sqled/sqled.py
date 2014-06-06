import sys

import wx
import wx.stc
import wx.gizmos
import wx.grid

import pginterface
#import sybinterface


VERSION = '0.1'

SQL_KEYWORDS = ['select', 'insert', 'update', 'delete', 'create', 'table', 'schema', 'not', 'null',
        'primary', 'key', 'unique', 'index', 'constraint', 'check', 'or', 'and', 'on', 'foreign', 'references',
        'cascade', 'default', 'grant', 'usage', 'to', 'is', 'restrict', 'into', 'values', 'from', 'where', 'group',
        'by', 'join', 'left', 'right', 'outer', 'having', 'distinct', 'as', 'limit', 'like', 'order']

faces = { 'times': 'Times',
          'mono' : 'Courier',
          'helv' : 'Helvetica',
          'other': 'new century schoolbook',
          'size' : 12,
          'size2': 10,
         }


class SQLEditCtrl(wx.stc.StyledTextCtrl):
    def __init__(self, parent):
        wx.stc.StyledTextCtrl.__init__(self, parent, -1, style=wx.BORDER_NONE)
        self.SetUpEditor()
    
    def SetUpEditor(self):
        self.SetLexer(wx.stc.STC_LEX_SQL)
        self.SetKeyWords(0, ' '.join(SQL_KEYWORDS))
        self.SetProperty('fold', '1')
        self.SetProperty('tab.timmy.whinge.level', '1')
        self.SetMargins(2, 2)
        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 40)
        self.SetIndent(4)
        self.SetIndentationGuides(True)
        self.SetBackSpaceUnIndents(True)
        self.SetTabIndents(True)
        self.SetTabWidth(4)
        self.SetUseTabs(False)
        self.SetViewWhiteSpace(False)
        self.SetEOLMode(wx.stc.STC_EOL_LF)
        self.SetViewEOL(False)
        self.SetEdgeMode(wx.stc.STC_EDGE_NONE)
        self.SetMarginType(2, wx.stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, wx.stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)
        
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT,     "face:%(helv)s,size:%(size)d" % faces)
        self.StyleClearAll()  # Reset all to be like the default

        # Global default styles for all languages
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT,     "face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)
        self.StyleSetSpec(wx.stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")

        try:
            self.StyleSetSpec(wx.stc.STC_SQL_COMMENT, "fore:#7F7F7F,size:%(size)d" % faces)
            self.StyleSetSpec(wx.stc.STC_SQL_COMMENTLINE, "fore:#007F00,face:%(other)s,size:%(size)d" % faces)
            self.StyleSetSpec(wx.stc.STC_SQL_WORD, "fore:#00007F,bold,size:%(size)d" % faces)
        except:
            self.StyleSetSpec(1, "fore:#7F7F7F,size:%(size)d" % faces)
            self.StyleSetSpec(5, "fore:#00007F,bold,size:%(size)d" % faces)
        
        """STC_SQL_CHARACTER
        STC_SQL_COMMENT
        STC_SQL_COMMENTDOC
        STC_SQL_COMMENTDOCKEYWORD
        STC_SQL_COMMENTDOCKEYWORDERROR
        STC_SQL_COMMENTLINE
        STC_SQL_COMMENTLINEDOC
        STC_SQL_DEFAULT
        STC_SQL_IDENTIFIER
        STC_SQL_NUMBER
        STC_SQL_OPERATOR
        STC_SQL_QUOTEDIDENTIFIER
        STC_SQL_SQLPLUS
        STC_SQL_SQLPLUS_COMMENT
        STC_SQL_SQLPLUS_PROMPT
        STC_SQL_STRING
        STC_SQL_USER1
        STC_SQL_USER2
        STC_SQL_USER3
        STC_SQL_USER4
        STC_SQL_WORD
        STC_SQL_WORD2"""

    def ShowPosition(self, pos):
        line = self.LineFromPosition(pos)
        #self.EnsureVisible(line)
        self.GotoLine(line)

    def GetRange(self, start, end):
        return self.GetTextRange(start, end)
        
    def GetLastPosition(self):
        return self.GetLength()


class SQLTreeCtrl(wx.gizmos.TreeListCtrl):
    def __init__(self, parent):
        wx.gizmos.TreeListCtrl.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE)

        self.AddColumn("Object")
        self.AddColumn("Type")
        
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded)
        
    def populate(self, db):
        self.root = self.AddRoot("Databases")
        self.SetPyData(self.root, db.get_root())
        fakeitem = self.AppendItem(self.root, '*fake*')
        self.populate_item(self.root)

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
        
        params = {'dbname': 'DATABASE', 'host': 'HOST', 'user': 'USERNAME', 'password': 'PASSWORD'}
        self.db = pginterface.PGInterface(params)
        
        self.tree.populate(self.db)

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


def main():
    app = wx.PySimpleApp()
    frame = MainFrame()
    frame.Show(1)
    app.MainLoop()


if __name__ == '__main__':
    main()
