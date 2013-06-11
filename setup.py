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
from distutils.core import setup

NAME='ipsutils'
VERSION='0.6.0'
DESCRIPTION='Solaris 11 IPS packaging library'
LICENSE='GPL'
AUTHOR='Joseph Hunkeler'
AUTHOR_EMAIL='jhunk@stsci.edu'
URL='http://bitbucket.org/jhunkeler/ipsbuild.git'
PACKAGE_DATA = {
  'ipsutils': ['tpl/*.tpl'],
}
PACKAGES=['ipsutils', 'ipsutils/tpl']
SCRIPTS=['ipsbuild.py', 'ipsbuild-setuptree.py', 'ipsutils-newspec.py', 'ipsutils-sanity.py']
PLATFORMS=['sunos5', 'linux2', 'linux']

with open(os.path.join(NAME, 'version.py'), 'w+') as fp:
    fp.writelines("__version__ = '{0:s}'\n".format(VERSION))

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      license=LICENSE,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      package_data=PACKAGE_DATA,
      packages=PACKAGES,
      scripts=SCRIPTS,
      platforms=PLATFORMS
      )
