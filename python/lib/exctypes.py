import ctypes
from .lazy import lazy
from functools import partialmethod


class CArray:
    def __init__(self, size):
        self.array = (self.TYPE * size)()

    @property
    def array_t(self):
        return type(self.array)

    @lazy
    def buffer(self):
        length = ctypes.sizeof(self.array)
        ptr = ctypes.cast(ctypes.pointer(self.array), ctypes.POINTER(ctypes.c_char * length))
        return ptr.contents

    def to_bytes(self):
        return self.buffer.raw

    def __getattr__(self, name):
        return getattr(self.array, name)

    def __getitem__(self, key):
        return self.array.__getitem__(key)

    def __setitem__(self, key, value):
        return self.array.__setitem__(key, value)


class Uint8Array(CArray):
    TYPE = ctypes.c_uint8


class Uint16Array(CArray):
    TYPE = ctypes.c_uint16


class Uint32Array(CArray):
    TYPE = ctypes.c_uint32


class Uint64Array(CArray):
    TYPE = ctypes.c_uint64


def ival(value):
    if isinstance(value, ctypes._SimpleCData):
        value = value.value
    return value


class cint:
    def __int__(self):
        return self.value

    def __oct__(self):
        return oct(self.value)

    def __hex__(self):
        return hex(self.value)

    def _newfn(self, name, other):
        type_ = self.__class__
        if isinstance(other, cint):
            if other.MAX > self.MAX:
                type_ = other.__class__
            other = other.value
        return type_(getattr(self.value, name)(other))

    local = locals()
    for name in ('__add__', '__sub__', '__mul__', '__floordiv__', '__mod__', '__pow__', '__lshift__', '__rshift__',
            '__and__', '__or__', '__xor__', '__radd__', '__rsub__', '__rmul__', '__rmul__', '__rfloordiv__',
            '__rmod__', '__rdivmod__', '__rpow__', '__rlshift__', '__rrshift__', '__rand__', '__ror__', '__rxor__'):
        local[name] = partialmethod(_newfn, name)
    local['__truediv__'] = local['__floordiv__']
    local['__rtruediv__'] = local['__rfloordiv__']
    del local, name

    def __iadd__(self, other):
        self.value += ival(other)

    def __isub__(self, other):
        self.value -= ival(other)

    def __imul__(self, other):
        self.value *= ival(other)

    def __ifloordiv__(self, other):
        self.value /= ival(other)

    __itruediv__ = __ifloordiv__

    def __imod__(self, other):
        self.value %= ival(other)

    def __ipow__(self, other):
        self.value **= ival(other)

    def __ilshift__(self, other):
        self.value <<= ival(other)

    def __irshift__(self, other):
        self.value >>= ival(other)

    def __iand__(self, other):
        self.value &= ival(other)

    def __ior__(self, other):
        self.value |= ival(other)

    def __ixor__(self, other):
        self.value ^= ival(other)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return '%s(%d)' % (self.__class__.__name__, self.value)


class int8(cint, ctypes.c_int8):
    MAX = 127


class int16(cint, ctypes.c_int16):
    MAX = 32767


class int32(cint, ctypes.c_int32):
    MAX = 2147483647


class int64(cint, ctypes.c_int64):
    MAX = 9223372036854775807


class u8(cint, ctypes.c_uint8):
    MAX = 255


class u16(cint, ctypes.c_uint16):
    MAX = 65535


class u32(cint, ctypes.c_uint32):
    MAX = 4294967295


class u64(cint, ctypes.c_uint64):
    MAX = 18446744073709551615
