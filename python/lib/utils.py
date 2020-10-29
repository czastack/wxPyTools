import math
from lib import extypes


class Accumulator:
    """累加器"""
    def __init__(self, value=0):
        self.value = value

    def add(self, i):
        self.value += i
        return self.value

    def sub(self, i):
        self.value -= i
        return self.value

    def inc(self):
        return self.add(1)

    def dec(self):
        return self.sub(1)

    def __int__(self):
        return self.value

    __index__ = __int__


def float32(number):
    """浮点数保留6位小数"""
    return round(number, 6)


def round_s(number, ndigits=0):
    rate = 10 ** ndigits
    return math.floor(number * rate + 0.5) / rate


def tuple2rgb(rgbtuple):
    """颜色3元组转整型rgb"""
    return rgbtuple[0] << 16 | rgbtuple[1] << 8 | rgbtuple[2]


def rgb2tuple(rgb):
    """整型rgb转颜色3元组"""
    return ((rgb >> 16) & 0xff), ((rgb >> 8) & 0xff), (rgb & 0xff)


def rgb2bgr(rgb):
    """rgb颜色转bgr颜色"""
    return (rgb & 0xff) << 16 | ((rgb >> 8) & 0xff) << 8 | ((rgb >> 16) & 0xff)


def gen_values(items):
    """生成自然数元组"""
    return tuple(range(len(items)))


def gen_flag(items):
    """生成标记元组 1, 2, 4, 8..."""
    return tuple(1 << i for i in range(len(items)))


def flag_generator(n):
    """标记生成器"""
    return (1 << i for i in range(n))


_split_tuple_cache = extypes.LRUCache()


def split_tuple(options):
    """把(value, label)分开"""
    key = id(options)
    cached = _split_tuple_cache.get(key)
    if cached is not None:
        return cached
    if isinstance(options, dict):
        options = options.items()
    result = tuple(zip(*options))
    _split_tuple_cache.set(key, result)
    return result


def split_tuple_reverse(options):
    """把(label, value)分开"""
    a, b = split_tuple(options)
    return b, a


def prepare_option(choices, values):
    """预处理选项"""
    if values is None:
        if choices is not None:
            if not isinstance(choices, (list, tuple, dict)):
                choices = tuple(choices)
            if isinstance(choices, dict) or extypes.is_list_tuple(choices[0]):
                values, choices = split_tuple(choices)
    return choices, values


def dirfind(obj, text):
    """dir属性中查找"""
    return list(filter(lambda x: text in x, dir(obj)))


def compose(*decos):
    """合并装饰器"""
    def _deco(func):
        for deco in reversed(decos):
            func = deco(func)
        return func
    return _deco


def filter_kwargs(**kwargs):
    """过滤掉值为None的默认参数"""
    return {name: value for name, value in kwargs.items() if value is not None}
