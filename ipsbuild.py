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
import ipsutils
import argparse
import os


# Initialize argument parser
parser = argparse.ArgumentParser(description='Build Solaris 11 packages from .ips spec files')
parser.add_argument('--version', action="store_true", help='Show version information')
parser.add_argument('--verbose', action="store_true", help='Increased verbosity')
parser.add_argument('--nodepsolve', action="store_true", help='Disable dependency resolution')
parser.add_argument('--noalign', action="store_true", help='Disable permission alignment')
parser.add_argument('--lint', action="store_true", help='Enables deep packaging checks')
parser.add_argument('--fast', action="store_true", help='Use system tools to extract source archive')
parser.add_argument('spec', nargs='*', help='An ipsutils spec file')
args = parser.parse_args()

if args.version:
    print("{0:s}".format(ipsutils.__version__))
    exit(0)

# Record current path, because we change directories from within the class
# This way all spec files will be read
cwd = os.path.abspath(os.curdir)
if args.spec:
    for spec in args.spec:
        build = ipsutils.build.Build(os.path.abspath(spec), options=args)
        build.show_summary()
        build.controller.do_tasks()
        os.chdir(cwd)
else:
    print("For detailed usage information:\n\t--help or -h")
exit(0)
