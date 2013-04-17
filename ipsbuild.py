# Solaris 11 IPS
# Automate package creation

from pprint import pprint
from collections import deque
import subprocess
import shlex
import ConfigParser
import argparse
import string

class IPS_Config(object):
    def __init__(self, ipsfile):

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
            for line in file(ipsfile).readlines():
                parts = shlex.split(line)
                if key + ":" in parts:
                    key_dict[key] = parts[1]

        found_data = False
        code_section = ['%build', '%prep', '%install', '%files']
        for section in code_section:
            for line in file(ipsfile).readlines():
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

class IPS_Task(object):
    def __init__(self, task):
        if type(task) is not type(list):
            TypeError("task must be a list")

class IPS_Build(IPS_Config):
    def __init__(self, ipsfile):
        super(IPS_Build, self).__init__(ipsfile)
        self.task_queue = deque()
        for key in self.script_dict:
            for i in self.script_dict[key]:
                self.task_queue.append(IPS_Task(i))
        


testfile = "test.ips"
build = IPS_Build(testfile)
print build.task_queue
