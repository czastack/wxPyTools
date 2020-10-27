import collections
import types
import weakref


list_tuple = (list, tuple)


def is_list_tuple(obj):
    return isinstance(obj, list_tuple)


def astr(text):
    """确保是字符串类型"""
    return text if isinstance(text, str) else str(text)


class Dict(dict):
    __slots__ = ('__dict__',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


class RichDict(Dict):
    """
    usage:
        data = RichDict({'a': 1})
        print(data.a)  # get 1
    """
    __slots__ = ('dafault_value',)

    def __init__(self, *args, dafault_value=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.dafault_value = dafault_value

    def __missing__(self, name):
        return self.dafault_value

    def __getattr__(self, name):
        return self.dafault_value

    def __getitem__(self, key):
        if isinstance(key, tuple):
            return (Dict.__getitem__(self, k) for k in key)
        elif isinstance(key, list):
            return [Dict.__getitem__(self, k) for k in key]
        return Dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if is_list_tuple(key):
            if is_list_tuple(value):
                get = iter(value).__next__
            else:
                def get():
                    return value
            for k in key:
                Dict.__setitem__(self, k, get())
        else:
            Dict.__setitem__(self, key, value)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, Dict.__repr__(self))

    def __and__(self, keys):
        if is_list_tuple(keys):
            return self.__class__({key: Dict.__getitem__(self, key) for key in keys})


class INum:
    def __init__(self, i):
        self.i = i

    def __pos__(self):
        self.i += 1
        return self.i

    def __neg__(self):
        self.i -= 1
        return self.i

    def __int__(self):
        return self.i

    __index__ = __int__


class WeakBinder:
    def __init__(self, obj):
        self.ref = weakref.proxy(obj)

    def __getattr__(self, name):
        attr = getattr(self.ref.__class__, name, None)
        if isinstance(attr, types.FunctionType):
            method = types.MethodType(attr, self.ref)
            setattr(self, name, method)
            return method
        return getattr(self.ref, name)


def weakmethod(method):
    if isinstance(method, types.MethodType):
        method = types.MethodType(method.__func__, weakref.proxy(method.__self__))
    return method


class classproperty:
    """类属性"""
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, instance, owner):
        return self.fget(owner)


class DataClassMeta(type):
    """数据类元类"""
    def __new__(cls, name, bases, attrs):
        fields = attrs.pop('fields', None)

        dataclass_bases = []

        if bases:
            for base in reversed(bases):
                if base != DataClass and issubclass(base, DataClass):
                    dataclass_bases.append(base)

        if dataclass_bases:
            # 处理继承
            base_slots = []
            base_defaults = {}
            defaults = attrs.get('defaults', None)
            for base in dataclass_bases:
                base_slots.extend(base.__slots__)
                if base.defaults:
                    base_defaults.update(base.defaults)
            if defaults:
                base_defaults.update(defaults)
            attrs['defaults'] = base_defaults
            if fields:
                base_slots.extend(fields)
            slots = base_slots
        else:
            slots = tuple(fields) if fields else ()
            attrs.setdefault('defaults', None)
        attrs['__slots__'] = slots
        return super().__new__(cls, name, bases, attrs)


class DataClass(metaclass=DataClassMeta):
    """数据类"""
    default = None

    def __init__(self, *args, **kwargs):
        self._set_data(args, kwargs)
        self.oninit()

    def oninit(self):
        """初始化"""
        pass

    def set_data(self, *args, **kwargs):
        self._set_data(args, kwargs)
        return self

    def _set_data(self, args, kwargs):
        for field, arg in zip(self.__slots__, args):
            setattr(self, field, arg)
        for field in kwargs:
            setattr(self, field, kwargs[field])

    def to_dict(self):
        return {field: getattr(self, field) for field in self.__slots__}

    def to_tuple(self):
        return tuple(self)

    def clone(self):
        return self.__class__(*self)

    def __iter__(self):
        return (getattr(self, field) for field in self.__slots__)

    def __getitem__(self, i):
        key = i if isinstance(i, str) else self.__slots__[i]
        return getattr(self, key, self.default)

    def __setitem__(self, i, value):
        key = i if isinstance(i, str) else self.__slots__[i]
        return setattr(self, key, value)

    def __str__(self):
        return str(self.to_tuple())

    def __repr__(self):
        return self.__class__.__name__ + self.__str__()

    def __getattr__(self, name):
        if self.defaults:
            return self.defaults.get(name, self.default)
        return self.default


def new_dataclass(name, fields, default=None, defaults=None, attrs=None, bases=None):
    """ 直接构造数据类
    :param bases: 父类元组或None"""
    the_attrs = {'fields': fields, 'default': default, 'defaults': defaults}
    if attrs:
        attrs.update(the_attrs)
        the_attrs = attrs
    if bases is None:
        bases = (DataClass,)
    elif DataClass not in bases:
        bases = (*bases, DataClass)
    return DataClassMeta(name, bases, the_attrs)


class LRUCache:
    """lru缓存"""
    __slots__ = ('size', 'cache')

    def __init__(self, size=8):
        self.size = size
        self.cache = collections.OrderedDict()

    def get(self, key):
        if key in self.cache:
            val = self.cache.pop(key)
            self.cache[key] = val
        else:
            val = None

        return val

    def set(self, key, val):
        if key in self.cache:
            val = self.cache.pop(key)
            self.cache[key] = val
        else:
            if self.size and len(self.cache) == self.size:
                self.cache.popitem(last=False)
            self.cache[key] = val
