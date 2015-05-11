import wx
import wx.stc

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
