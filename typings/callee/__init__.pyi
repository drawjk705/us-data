"""
This type stub file was generated by pyright.
"""

from callee.attributes import Attr, Attrs, HasAttr, HasAttrs

from callee.base import And, Either, Eq, Is, IsNot, Matcher, Not, OneOf, Or, Xor
from callee.collections import (
    Dict,
    Generator,
    Iterable,
    List,
    Mapping,
    OrderedDict,
    Sequence,
    Set,
)
from callee.functions import Callable, CoroutineFunction, Function, GeneratorFunction
from callee.general import Any, ArgThat, Captor, Matching
from callee.numbers import (
    Complex,
    Float,
    Fraction,
    Int,
    Integer,
    Integral,
    Long,
    Number,
    Rational,
    Real,
)
from callee.objects import Bytes, Coroutine, FileLike
from callee.operators import (
    Contains,
    Ge,
    Greater,
    GreaterOrEqual,
    GreaterOrEqualTo,
    GreaterThan,
    Gt,
    In,
    Le,
    Less,
    LessOrEqual,
    LessOrEqualTo,
    LessThan,
    Longer,
    LongerOrEqual,
    LongerOrEqualTo,
    LongerThan,
    Lt,
    Shorter,
    ShorterOrEqual,
    ShorterOrEqualTo,
    ShorterThan,
)
from callee.strings import EndsWith, Glob, Regex, StartsWith, String, Unicode
from callee.types import Class, Inherits, InstanceOf, IsA, SubclassOf, Type

"""
callee
"""
__version__ = "0.3.1"
__description__ = "Argument matchers for unittest.mock"
__author__ = "Karol Kuczmarski"
__license__ = "BSD"
