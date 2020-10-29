"""
Python port of the extended Node.js EventEmitter
"""

from collections import defaultdict


class EventEmitter:
    default_max_listeners = -1

    def __init__(self, max_listeners=default_max_listeners):
        """The EventEmitter class"""
        self._events = defaultdict(list)
        self.max_listeners = max_listeners

    def add_listener(self, event, listener, prepend=False):
        """添加事件监听
        :returns: 是否添加成功
        """
        listeners = self._events[event]
        if not isinstance(listener, Listener):
            for item in listeners:
                if item.func == listener:
                    return False

            listener = Listener(listener, event)
        else:
            if listener in listeners:
                return False
        if prepend:
            listeners.insert(0, listener)
        else:
            listeners.append(listener)
        return True

    def on(self, event, func=None, ttl=-1):
        """
        注册事件
        :param event: 事件名称
        :param func: 监听函数, 为None时作为装饰器
        :param ttl: 活跃次数, -1为无限
        """
        def _on(func):
            listener = Listener(func, event, ttl)
            self.add_listener(event, listener)

            return self

        if func is not None:
            return _on(func)
        else:
            return _on

    def once(self, event, func=None):
        """
        注册单次事件监听
        """
        return self.on(event, func, 1)

    def prepend_listener(self, event, func=None, ttl=-1):
        """注册事件插到开头"""
        def _on(func):
            listener = Listener(func, event, ttl)
            self.add_listener(event, listener, prepend=True)

            return self

        if func is not None:
            return _on(func)
        else:
            return _on

    def prepend_onece_listener(self, event, func=None):
        """
        注册单次事件监听
        """
        return self.prepend_listener(event, func, 1)

    def remove_listener(self, event, listener):
        """
        移除事件监听
        """
        listeners = self._events[event]
        if not isinstance(listener, Listener):
            for item in listeners:
                if item.func == listener:
                    listeners.remove(item)
                    break
        else:
            if listener in listeners:
                listeners.remove(item)
        return self

    def off(self, event, func=None):
        """
        移除事件
        :param event: 事件名称
        :param func: 监听函数, 为None时作为装饰器
        """
        def _off(func):
            self.remove_listener(event, func)

            return self

        if func is not None:
            return _off(func)
        else:
            return _off

    def remove_all_listeners(self, event):
        """移除所有指定事件监听"""
        self._events[event].clear()

    def listeners(self, event):
        """获取指定事件的监听"""
        return self._events[event]

    def event_names(self):
        return self._events.keys()

    def emit(self, event, *args, **kwargs):
        """
        触发事件
        """
        listeners = self._events[event]
        remove_list = []

        for listener in listeners:
            if not listener(*args, **kwargs):
                # ttl为0，需要移除
                remove_list.append(listener)

        for listener in remove_list:
            listeners.remove(listener)


class Listener(object):
    """监听器"""

    def __init__(self, func, event=None, ttl=-1):
        """
        监听器初始化
        """
        super(Listener, self).__init__()

        self.func = func
        self.event = event
        self.ttl = ttl

    def __call__(self, *args, **kwargs):
        """
        调用
        """
        self.func(*args, **kwargs)

        if self.ttl > 0:
            self.ttl -= 1
            if self.ttl == 0:
                return False

        return True


if __name__ == "__main__":
    def main():
        event = EventEmitter()

        @event.on('test')
        def test():
            print('test emited')

        event.emit('test')

    main()
