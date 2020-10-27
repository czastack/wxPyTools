class ProxyMetaclass(type):

    def __new__(cls, name, bases, attrs):
        magic = attrs.pop('__magic__', None)

        if magic:
            for key in magic:
                key = "__%s__" % key
                fn = getattr(Magic, key, None)

                if fn:
                    attrs[key] = fn
                else:
                    code = "def {0}(self, *args): return self.proxy.{0}(*args)".format(key)
                    exec(code, None, attrs)
                    setattr(Magic, key, attrs[key])

        return super().__new__(cls, name, bases, attrs)


class Proxy(metaclass=ProxyMetaclass):
    """
    classfield __proxy__: name of proxy member
    classfield __magic__: list of magic function name without under line
    """
    def __init__(self, obj=None):
        object.__setattr__(self, self.__proxy__, obj)

    @property
    def proxy(self):
        return getattr(self, self.__proxy__)

    def __getattr__(self, name):
        return getattr(self.proxy, name)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, str(self.proxy))


class Magic:
    @property
    def proxy(self):
        raise NotImplementedError

    def __str__(self):
        return self.proxy.__str__()

    def __iter__(self):
        return self.proxy.__iter__()

    def __next__(self):
        return self.proxy.__next__()

    def __getitem__(self, key):
        return self.proxy[key]

    def __setitem__(self, key, value):
        self.proxy[key] = value

    def __delitem__(self, key):
        del self.proxy[key]

    def __delattr__(self, key):
        self.proxy.__delattr__(key)

    def __and__(self, arg):
        return self.proxy.__and__(arg)

    def __or__(self, arg):
        return self.proxy.__or__(arg)


if __name__ == '__main__':
    class Target:
        def __pos__(self):
            return 1

    class Test(Proxy):
        __proxy__ = '_data'
        __magic__ = ('pos', 'str')

    p = Test(Target())
    print(p)
    print(+p)
