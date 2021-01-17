"""
This type stub file was generated by pyright.
"""

from .std import tqdm as std_tqdm

"""
IPython/Jupyter Notebook progressbar decorator for iterators.
Includes a default `range` iterator printing to `stderr`.

Usage:
>>> from tqdm.notebook import trange, tqdm
>>> for i in trange(10):
...     ...
"""
if True:
    IPY = 0
    IPYW = 0
__author__ = { "github.com/": ["lrq3000", "casperdcl", "alexanderkuk"] }
class TqdmHBox(HBox):
    """`ipywidgets.HBox` with a pretty representation"""
    def __repr__(self, pretty=...):
        ...
    


class tqdm_notebook(std_tqdm):
    """
    Experimental IPython/Jupyter Notebook widget using tqdm!
    """
    @staticmethod
    def status_printer(_, total=..., desc=..., ncols=...):
        """
        Manage the printing of an IPython/Jupyter Notebook progress bar widget.
        """
        ...
    
    def display(self, msg=..., pos=..., close=..., bar_style=...):
        ...
    
    @property
    def colour(self):
        ...
    
    @colour.setter
    def colour(self, bar_color):
        ...
    
    def __init__(self, *args, **kwargs) -> None:
        """
        Supports the usual `tqdm.tqdm` parameters as well as those listed below.

        Parameters
        ----------
        display  : Whether to call `display(self.container)` immediately
            [default: True].
        """
        ...
    
    def __iter__(self, *args, **kwargs):
        ...
    
    def update(self, *args, **kwargs):
        ...
    
    def close(self, *args, **kwargs):
        ...
    
    def clear(self, *_, **__):
        ...
    
    def reset(self, total=...):
        """
        Resets to 0 iterations for repeated use.

        Consider combining with `leave=True`.

        Parameters
        ----------
        total  : int or float, optional. Total to use for the new bar.
        """
        ...
    


def tnrange(*args, **kwargs):
    """
    A shortcut for `tqdm.notebook.tqdm(xrange(*args), **kwargs)`.
    On Python3+, `range` is used instead of `xrange`.
    """
    ...

tqdm = tqdm_notebook
trange = tnrange