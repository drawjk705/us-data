"""
This type stub file was generated by pyright.
"""

from .std import tqdm as std_tqdm

"""
GUI progressbar decorator for iterators.
Includes a default `range` iterator printing to `stderr`.

Usage:
>>> from tqdm.gui import trange, tqdm
>>> for i in trange(10):
...     ...
"""
__author__ = { "github.com/": ["casperdcl", "lrq3000"] }
class tqdm_gui(std_tqdm):
    """
    Experimental GUI version of tqdm!
    """
    def __init__(self, *args, **kwargs) -> None:
        ...
    
    def close(self):
        ...
    
    def clear(self, *_, **__):
        ...
    
    def display(self):
        ...
    


def tgrange(*args, **kwargs):
    """
    A shortcut for `tqdm.gui.tqdm(xrange(*args), **kwargs)`.
    On Python3+, `range` is used instead of `xrange`.
    """
    ...

tqdm = tqdm_gui
trange = tgrange
