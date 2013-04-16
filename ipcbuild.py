# Solaris 11 IPC
# Automate package creation

from pprint import pprint
import shlex
import ConfigParser
import argparse
import string

class FakeSecHead(object):
    """Found on stackoverflow, public domain code"""
    def __init__(self, fp):
        self.fp = fp
        self.sechead = '[IPC]\n'
    def readline(self):
        if self.sechead:
            try:
                return self.sechead
            finally:
                self.sechead = None
        else:
            return self.fp.readline()
'''
class IPC_Config(object):
    def __init__(self, ipcfile):
        self._header = 'IPC'
        self.config = ConfigParser.SafeConfigParser()
        self._config_read(ipcfile)
        print("{0:s} parsed".format(ipcfile))

    def __iter__(self):
        for i in self.config.items(self._header):
            yield i

    def __getitem__(self, option):
        return self.config.get(self._header, option)

    def _config_read(self, ipcfile):
        """Wrapper for FakeSecHead"""
        self.config.readfp(FakeSecHead(open(ipcfile)))
'''

class IPC_Config(object):
    def __init__(self, ipcfile):

        key_dict = {
                'name': '',
                'version': '',
                'release': '',
                'maintainer': '',
                'upstream_url': '',
                'description': '',
                'arch': '',
                'license': ''
                }

        script_dict = {
                  'build': [],
                  'prep': [],
                  'install': [],
                  'files': []
                  }

        for key in key_dict:
            for line in file(ipcfile).readlines():
                parts = shlex.split(line)
                if key + ":" in parts:
                    key_dict[key] = parts[1]

        found_data = False
        code_section = ['%build', '%prep', '%install', '%files']
        for section in code_section:
            for line in file(ipcfile).readlines():
                parts = shlex.split(line)
                if '%end' in parts:
                    found_data = False
                if section in parts:
                    found_data = True
                    continue
                if found_data:
                    script_dict[section.strip('%')].append(parts)


        self.key_dict = key_dict
        self.script_dict = script_dict

class IPC_Build(IPC_Config):
    def __init__(self, ipcfile):
        super(IPC_Build, self).__init__(ipcfile)
        print(self.key_dict['name'])


testfile = "test.ipc"
build = IPC_Build(testfile)

