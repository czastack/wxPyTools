import wx


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
