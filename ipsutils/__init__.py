import os.path
from . import env
from . import config
from . import build
from . import task


try:
    from version import __version__
except:
    __version__ = '0.0.0'

if __name__ == '__main__':
    pass