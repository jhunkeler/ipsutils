import os
import sys
from . import config


class Environment(config.Config):
    def __init__(self, ipsfile):
        super(Environment, self).__init__(ipsfile)
        if sys.platform == 'linux2' \
            or sys.platform == 'sunos5':
            self.__basepath = os.path.join(os.environ['HOME'], 'ipsbuild')
        else:
            self.__basepath = os.path.join(os.environ['USERPROFILE'], 'ipsbuild')
            
        self.env = {
                'IPSBUILD': self.pathgen(''),
                'BUILDROOT': self.pathgen('BUILDROOT'),
                'BUILD': self.pathgen('BUILD'),
                'SPECS': self.pathgen('SPECS'),
                'SOURCES': self.pathgen('SOURCES'),
                'PKGS': self.pathgen('PKGS'),
                'SPKGS': self.pathgen('SPKGS')
                }
        
        self.complete_name = self.key_dict['name'] + '-' + self.key_dict['version']
        self.env_pkg = {
                'BUILDROOT': os.path.join(self.env['BUILDROOT'], self.complete_name),
                'BUILD': os.path.join(self.env['BUILD'], self.complete_name),
                'SOURCES': os.path.join(self.env['SOURCES'], os.path.basename(self.key_dict['source_url'])),
                'PKGS': os.path.join(self.env['PKGS'], self.complete_name),
                'SPKGS': os.path.join(self.env['SPKGS'], self.complete_name)
                }

        self.tool = {
                    'tar': 'tar',
                    'unzip': 'unzip',
                    'gunzip': 'gunzip',
                    'bunzip': 'bunzip'
                    }

        if sys.platform == 'sunos5':
            self.tool['tar'] = 'gtar'

    def pathgen(self, path):
        return os.path.join(self.__basepath, path)
