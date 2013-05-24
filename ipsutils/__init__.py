import os.path
from . import env
from . import config
from . import build
from . import task


if os.path.exists(os.path.join('ipsutils', 'version.py')):
    from version import __version__
else:
    __version__ = '0.0.0'

if __name__ == '__main__':
    pass