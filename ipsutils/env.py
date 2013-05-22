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
from . import config


class Environment(config.Config):
    def __init__(self, ipsfile):
        super(Environment, self).__init__(ipsfile)

        # Platform specific ipsbuild directory assignment
        if sys.platform == 'linux2' \
            or sys.platform == 'sunos5':
            self.__basepath = os.path.join(os.environ['HOME'], 'ipsbuild')
        else:
            self.__basepath = os.path.join(os.environ['USERPROFILE'], 'ipsbuild')

        # Dictionary of top-level directories
        self.env = {
                'IPSBUILD': self.pathgen(''),
                'BUILDROOT': self.pathgen('BUILDROOT'),
                'BUILD': self.pathgen('BUILD'),
                'SPECS': self.pathgen('SPECS'),
                'SOURCES': self.pathgen('SOURCES'),
                'PKGS': self.pathgen('PKGS'),
                'SPKGS': self.pathgen('SPKGS')
                }
        # complete_name is required to build proper path names.  
        # The use of "self" in this case may be deprecated in the future.
        self.complete_name = self.key_dict['name'] + '-' + self.key_dict['version']
        # Dictionary of package-level directories
        self.env_pkg = {
                'BUILDROOT': os.path.join(self.env['BUILDROOT'], self.complete_name),
                'BUILDPROTO': os.path.join(self.env['BUILDROOT'], self.complete_name, 'proto_install'),
                'BUILD': os.path.join(self.env['BUILD'], self.complete_name),
                'SOURCES': os.path.join(self.env['SOURCES'], os.path.basename(self.key_dict['source_url'])),
                'PKGS': os.path.join(self.env['PKGS'], self.complete_name),
                'SPKGS': os.path.join(self.env['SPKGS'], self.complete_name)
                }

        self.env_meta = {
                'TRANS': os.path.join(self.env_pkg['BUILDROOT'], self.complete_name + '.mog'),
                'FILES': os.path.join(self.env_pkg['BUILDROOT'], self.complete_name + '.p5m.1'),
                'FILES_PASS2': os.path.join(self.env_pkg['BUILDROOT'], self.complete_name + '.p5m.2'),
                'DEPENDS': os.path.join(self.env_pkg['BUILDROOT'], self.complete_name + '.p5m.3'),
                'DEPENDSOLVE': os.path.join(self.env_pkg['BUILDROOT'], self.complete_name + '.p5m.3.res')
                }
        # Generic utility mapping for platform specific configuration.
        # Note: This is mainly to test script functionality on different platforms
        #       even though this library is VERY VERY Solaris 11 specific
        self.tool = {
                    'tar': 'tar',
                    'unzip': 'unzip',
                    'gunzip': 'gunzip',
                    'bunzip': 'bunzip',
                    'pkgsend': 'pkgsend',
                    'pkgmogrify': 'pkgmogrify',
                    'pkgdepend': 'pkgdepend',
                    'pkgfmt': 'pkgfmt'
                    }

        # Oracle Solaris tar is ancient.  GNU tar is preferrred.
        if sys.platform == 'sunos5':
            self.tool['tar'] = 'gtar'

    def pathgen(self, path):
        """Simplify path generation based on "ipsbuild" base path
        
        path: directory leaf of 'ipsbuild' directory (in $HOME)
        """
        return os.path.join(self.__basepath, path)
