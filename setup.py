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

from distutils.core import setup

setup(name='ipsutils',
      version='0.1.0',
      description='Solaris 11 IPS packaging library',
      license='GPL',
      author='Joseph Hunkeler',
      author_email='jhunk@stsci.edu',
      url='http://www.stsci.edu/~jhunk/ips',
      packages=['ipsutils'],
      scripts={'ipsbuild.py', 'ipsbuild-setuptree.py'},
      platforms=['sunos5', 'linux2']
      )
