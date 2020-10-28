import os
import sys
import traceback
import wx
import wx.py
from wx.py.pseudo import PseudoFileOut, PseudoFileErr
from common import DATA_DIR


class MyShell(wx.py.shell.Shell):
    """修补过的Shell"""

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        controlDown = event.ControlDown()
        rawControlDown = event.RawControlDown()
        currpos = self.GetCurrentPos()

        if (rawControlDown or controlDown) and key == wx.WXK_BACK:
            if self.GetRange(self.promptPosEnd, currpos).isspace():
                self.DeleteRange(self.promptPosEnd, currpos - self.promptPosEnd)
                return

        super().OnKeyDown(event)


class BottomPane(wx.Notebook):
    """
    底部面板
    """
    def __init__(self, parent, *args, **kwargs):
        wx.Notebook.__init__(self, parent, *args, **kwargs)

        self.outputWindow = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_WORDWRAP)
        self.AddPage(self.outputWindow, '输出')
        self.shell = MyShell(self, execStartupScript=False)
        self.AddPage(self.shell, '控制台')

        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnClose)

        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.redirectStdout()
        self.redirectStderr()

        self.historyPath = os.path.join(DATA_DIR, 'python_history')
        self.LoadHistory()

    def LoadSettings(self, config):
        """
        加载配置
        """
        self.config = config
        self.shell.LoadSettings(self.config)

    def SaveHistory(self):
        """保存shell历史"""
        try:
            enc = 'utf-8'
            hist = b'\x00\n'.join([h.encode('utf-8') for h in self.shell.history])
            with open(self.historyPath, 'wb') as f:
                f.write(hist)
        except Exception:
            d = wx.MessageDialog(self, "Error saving history file.",
                                 "Error", wx.ICON_EXCLAMATION | wx.OK)
            d.ShowModal()
            d.Destroy()
            raise

    def LoadHistory(self):
        if os.path.exists(self.historyPath):
            try:
                with open(self.historyPath, 'rb') as f:
                    hist = f.read()

                hist = [h.decode('utf-8') for h in hist.split(b'\x00\n')]
                self.shell.history = hist
                wx.py.dispatcher.send(signal="Shell.loadHistory",
                                history=self.shell.history)
            except Exception:
                traceback.print_exc()

                d = wx.MessageDialog(self, "Error loading history file.",
                                     "Error", wx.ICON_EXCLAMATION | wx.OK)
                d.ShowModal()
                d.Destroy()

    def OnClose(self, event):
        """Event handler for closing."""
        self.SaveHistory()
        self.redirectStdout(False)
        self.redirectStderr(False)
        if self.shell.waiting:
            if event.CanVeto():
                event.Veto(True)
        else:
            self.shell.destroy()

    def redirectStdout(self, redirect=True):
        """重定向标准输出"""
        if redirect:
            sys.stdout = PseudoFileOut(self.outputAppendText)
        else:
            sys.stdout = self.stdout

    def redirectStderr(self, redirect=True):
        """重定向标准错误"""
        if redirect:
            sys.stderr = PseudoFileErr(self.outputAppendText)
        else:
            sys.stderr = self.stderr

    def outputAppendText(self, text):
        self.outputWindow.AppendText(text)
