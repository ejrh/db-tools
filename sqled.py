import sys
import wx

from sqled import MainFrame

def main():
    app = wx.PySimpleApp()
    frame = MainFrame()
    frame.Show(1)
    app.MainLoop()


if __name__ == '__main__':
    main()
