import wx


def ParseMenuBar(owner, menubar, data):
    """
    递归解析添加菜单到wx.MenuBar
    owner: 拥有者
    menubar: wx.MenuBar
    data: list
    """
    for menudata in data:
        # 一级菜单
        menu = wx.Menu()
        children = menudata.get('children', None)
        if children:
            for childdata in children:
                ParseMenu(owner, menu, childdata)

        menubar.Append(menu, menudata['text'])


def ParseMenu(owner, parent, data):
    """
    递归解析添加菜单
    owner: 拥有者
    parent: wx.Menu
    data: dict
    """
    children = data.get('children', None)
    if children is None:
        # 单个菜单项
        if data['text'] == '-':
            parent.AppendSeparator()
        else:
            menuItem = wx.MenuItem(parent, wx.ID_ANY, data['text'], data.get(
                'help', wx.EmptyString), data.get('kind', wx.ITEM_NORMAL))
            parent.Append(menuItem)
            # 注册事件
            handler = data.get('handler', None)
            if handler:
                if isinstance(handler, str):
                    handler = getattr(owner, handler)
                owner.Bind(wx.EVT_MENU, handler, menuItem)
    else:
        # 子菜单
        submenu = wx.Menu()
        parent.AppendSubMenu(submenu, data['text'])
        for childdata in children:
            ParseMenu(owner, submenu, childdata)


def choose_file(msg, dir, file, wildcard=wx.FileSelectorDefaultWildcardStr, mustExist=False):
    """选择文件"""
    flag = wx.FD_OPEN
    if mustExist:
        flag |= wx.FD_FILE_MUST_EXIST
    dialog = wx.FileDialog(None, msg, dir, file, wildcard, flag)
    if dialog.ShowModal() == wx.ID_CANCEL:
        return wx.NoneString

    return dialog.GetPath()


def json_dump_file(owner, data, dumper=None):
    """选择json文件导出"""
    lastfile = owner and getattr(owner, 'lastfile', None)
    path = choose_file("选择保存文件", file=lastfile, wildcard='*.json')
    if path:
        if owner:
            owner.lastfile = path
        with open(path, 'w', encoding="utf-8") as file:
            if dumper is None:
                json.dump(data, file)
            else:
                dumper(data, file)


def json_load_file(owner):
    """选择json文件导入"""
    lastfile = owner and getattr(owner, 'lastfile', None)
    path = choose_file("选择读取文件", file=lastfile, wildcard='*.json')
    if path:
        if owner:
            owner.lastfile = path
        with open(path, encoding="utf-8") as file:
            return json.load(file)
