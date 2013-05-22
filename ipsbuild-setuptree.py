#!/usr/bin/env python
# This file is part of ipsutils.

# ipsutils is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ipsutils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ipsutils.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

home = None
try:
    if sys.platform == 'linux2' \
        or sys.platform == 'linux' \
        or sys.platform == 'sunos5':
        home = os.path.normpath(os.environ['HOME'])
    elif sys.platform == 'win32':
        home = os.path.normpath(os.environ['USERPROFILE'])
except:
    Exception("Unsupported platform: {0:s}".format(sys.platform))

head = os.path.join(home, 'ipsbuild')
tree = ['BUILDROOT',
        'BUILD',
        'SPECS',
        'SOURCES',
        'PKGS',
        'SPKGS']

def create_dir(dirent):
    print("Creating directory: {0:s}".format(dirent))
    os.mkdir(dirent)

def main():
#    try:
    create_dir(head)
#    except:
#        print("{0:s} already exists, please remove it.".format(head))

    try:
        for d in tree:
            create_dir(os.path.join(head, d))
    except:
        pass

if __name__ == '__main__':
    main()
