import os
import sys
import types
import wx
import wx.aui

from dataclasses import dataclass
from typing import List
from common import CONF_DIR
from widgets.bottompane import BottomPane
from lib.wxutils import ParseMenu


class MainFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title='主窗口', style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSize(self.FromDIP(wx.Size(640, 960)))
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.mgr = wx.aui.AuiManager(self)
        self.mgr.SetFlags(wx.aui.AUI_MGR_DEFAULT)

        self.Freeze()
        self.menubar = wx.MenuBar(0)
        self.InitMenuBar()
        self.SetMenuBar(self.menubar)

        self.statusBar = self.CreateStatusBar(1, wx.STB_SIZEGRIP, wx.ID_ANY)

        self.auiToolBar = wx.aui.AuiToolBar(self, size=self.FromDIP(wx.Size(-1, 50)), style=(
            wx.aui.AUI_TB_TEXT))
        self.InitToolBar()
        self.mgr.AddPane(self.auiToolBar, wx.aui.AuiPaneInfo().Top().CaptionVisible(False).CloseButton(False))

        self.notebook = wx.aui.AuiNotebook(self)
        self.mgr.AddPane(self.notebook, wx.aui.AuiPaneInfo().Center().CaptionVisible(False).CloseButton(False))

        self.bottomPane = BottomPane(self, size=self.FromDIP(wx.Size(-1, 150)))
        self.mgr.AddPane(self.bottomPane, wx.aui.AuiPaneInfo().Name("bottom").Bottom().CloseButton(
            False).MaximizeButton(True))

        self.mgr.Update()
        self.Centre(wx.BOTH)

        self.Thaw()

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.LoadSettings()

        self.tool_tree = None

    def LoadSettings(self):
        """
        加载配置
        """
        fileName = os.path.join(CONF_DIR, 'config.ini')
        self.config = wx.FileConfig(localFilename=fileName)
        self.config.SetRecordDefaults(True)

        self.bottomPane.LoadSettings(self.config)

    def OnClose(self, event):
        """Event handler for closing."""
        if self.bottomPane.shell.waiting:
            if event.CanVeto():
                event.Veto(True)
        else:
            self.bottomPane.shell.destroy()
            self.mgr.UnInit()
            event.Skip()

    def InitMenuBar(self):
        """初始化菜单"""
        data = [
            {
                "text": "文件",
                "help": "文件操作",
                "children": [
                    {"text": "打开文件\tCtrl+O"},
                    {"text": "-"},
                    {"text": "关闭窗口\tCtrl+W", "handler": "OnCloseWindow"},
                    {"text": "重启\tCtrl+R", "handler": "OnRestart"},
                    {"text": "退出\tCtrl+Q", "handler": "OnQuit"},
                ]
            },
            {
                "text": "工具",
                "children": [
                    {"text": "打开工具\tCtrl+Shift+P", "handler": "OnOpenTool"},
                ]
            },
            {
                "text": "视图",
                "children": [
                    {"text": "保存窗口位置和大小"},
                    {"text": "切换控制台\tCtrl+`", "handler": "OnToggleBottom"},
                ]
            },
        ]

        for menudata in data:
            # 一级菜单
            menu = wx.Menu()
            children = menudata.get('children', None)
            if children:
                for childdata in children:
                    ParseMenu(self, menu, childdata)

            self.menubar.Append(menu, menudata['text'])

    def InitToolBar(self):
        """初始化工具"""
        tool = self.auiToolBar.AddTool(wx.ID_ANY, "打开工具", wx.NullBitmap, wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None)
        self.Bind(wx.EVT_MENU, self.OnOpenTool, tool)
        self.auiToolBar.Realize()

    # 菜单事件

    def OnCloseWindow(self, event):
        """关闭窗口"""
        self.Close()

    def OnRestart(self, event):
        """重启"""
        argv = list(sys.argv)
        if os.path.basename(sys.executable) not in argv[0]:
            argv.insert(0, sys.executable)
        cmdline = ' '.join(argv)
        if wx.Execute(cmdline):
            self.Close()

    def OnQuit(self, event):
        """退出"""
        self.Close()
        app.ExitMainLoop()

    def OnOpenTool(self, event):
        """打开工具对话框"""
        dialog = getattr(self, 'tool_dialog', None)
        if dialog is None:
            dialog = wx.Dialog(self, wx.ID_ANY, "打开工具", wx.DefaultPosition, self.FromDIP(
                wx.Size(480, 640)), wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
            sizer = wx.BoxSizer(wx.VERTICAL)

            # 工具树控件
            self.tool_tree = wx.TreeCtrl(dialog, style=(
                wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_TWIST_BUTTONS))
            sizer.Add(self.tool_tree, 1, wx.EXPAND | wx.ALL, 5)

            self.tool_tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnToolItemActivated)

            # 加载tools模块
            import tools
            root = self.tool_tree.AddRoot("")
            root_tools = self.get_sub_tools(tools)
            for item in root_tools:
                item.id = self.tool_tree.AppendItem(root, item.text, data=item)

            # 对话框底部按钮
            okay = wx.Button(dialog, wx.ID_OK)
            okay.SetDefault()
            # cancel = wx.Button(dialog, wx.ID_CANCEL)
            btns = wx.StdDialogButtonSizer()
            btns.AddButton(okay)
            # btns.AddButton(cancel)
            btns.Realize()
            sizer.Add(btns, 0, wx.EXPAND | wx.ALL, 5)

            dialog.SetSizer(sizer)
            # sizer.Fit(dialog)
        dialog.ShowModal()

    def OnToggleBottom(self, event):
        """显示/隐藏底栏"""
        pane = self.mgr.GetPane("bottom")
        pane.Show(not pane.IsShown())
        self.mgr.Update()

    def OnToolItemActivated(self, event):
        """打开工具选项框项选中"""
        item = event.GetItem()
        itemdata = self.tool_tree.GetItemData(item)
        if itemdata.package:
            if not itemdata.children:
                itemdata.children = self.get_sub_tools(itemdata.module)
                for child in itemdata.children:
                    child.id = self.tool_tree.AppendItem(itemdata.id, child.text, data=child)
            self.tool_tree.Toggle(item)
        else:
            self.open_tool_by_name(itemdata.module)
            self.tool_dialog.EndModal()

    def get_sub_tools(self, parent):
        """获取子目录工具"""
        dir_path = os.path.dirname(parent.__file__)
        files = os.listdir(dir_path)
        result = []
        for file in files:
            if not file.startswith('__') and file.find('.') == -1 and os.path.isdir(os.path.join(dir_path, file)):
                module = __import__(parent.__name__ + '.' + file, fromlist=file)
                name = getattr(module, 'name', None)
                if name is not None:
                    result.append(ToolTreeItem(module, name, getattr(module, 'package', False)))
        return result

    def get_tool(self, name):
        """根据名称获取工具类"""
        name = name.__name__ if isinstance(name, types.ModuleType) else 'tools.' + name
        module = __import__(name, fromlist=['main']).main
        return module.Main

    def open_tool_by_name(self, name):
        """根据名称打开工具"""
        Tool = self.get_tool(name)
        try:
            tool = Tool(self.notebook)
        except Exception as e:
            traceback.print_exc()


@dataclass
class ToolTreeItem:
    """工具节点数据"""
    module: str
    text: str
    package: str
    id: int = -1
    children: List['ToolTreeItem'] = None


if __name__ == "__main__":
    app = wx.App()
    frm = MainFrame(None)
    frm.Show()
    app.MainLoop()
