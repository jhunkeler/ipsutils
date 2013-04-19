# Solaris 11 IPS
# Automate package creation

from pprint import pprint
import subprocess
import shlex
import argparse
import string
import sys
import os

class IPS_Environment(object):
    def __init__(self):
        super(IPS_Environment, self).__init__()
        self._basepath = os.path.join(os.environ['HOME'], 'ipsbuild')
        self.env = {
                'BUILDROOT': self.pathgen('BUILDROOT'),
                'BUILD': self.pathgen('BUILD'),
                'SPECS': self.pathgen('SPECS'),
                'SOURCES': self.pathgen('SOURCES'),
                'PKGS': self.pathgen('PKGS'),
                'SPKGS': self.pathgen('SPKGS')
                }

        self.tool = {
                    'tar': 'tar',
                    'unzip': 'unzip',
                    'gunzip': 'gunzip',
                    'bunzip': 'bunzip'
                    }

        if sys.platform == 'solaris':
            self.tool['tar'] = 'gtar'


    def pathgen(self, path):
        return os.path.join(self._basepath, path)

class IPS_Config(object):
    def __init__(self, ipsfile):
        super(IPS_Config, self).__init__()
        key_dict = {
                'name': '',
                'version': '',
                'release': '',
                'maintainer': '',
                'group': '',
                'upstream_url': '',
                'source_url': '',
                'description': '',
                'summary': '',
                'classification': '',
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
        code_section = ['%build', '%prep', '%install']
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


class IPS_TaskController(list):
    def __init__(self):
        super(IPS_TaskController, self).__init__()
        self._store = []

    def task(self, task):
        super(IPS_TaskController, self).append(task)

    def do_tasks(self):
        for task in super(IPS_TaskController, self).__iter__():
            self._store.append(task.run())

class IPS_NamedTask(object):
    def __init__(self, name, task_list):
        if type(task_list) is not type(list):
            TypeError("task must be a list")

        self.name = name
        self.task = task_list

    def run(self):
        print("Running task: {0:s}".format(self.name))
        for step in self.task:
            print("+ {0:s}".format(step))

class IPS_Build(IPS_Config, IPS_Environment):
    def __init__(self, ipsfile):
        # Parent IPS_Config parses configuration data in .ips file
        # Inherited members are used to populate package information
        # as well as build tasks
        super(IPS_Build, self).__init__(ipsfile)
        # Um, super and multiple inheritance SUCKS... back to Python2 style
        #IPS_Environment.__init__(self)

        # Create list of build tasks
        ordered_tasks = ['prep', 'build', 'install']
        self.controller = IPS_TaskController()

        # Assign built-in IPS tasks
        self.controller.task(IPS_NamedTask('Extract source', self.source_unpack()))
        self.controller.task(IPS_NamedTask('Create buildroot', self.create_buildroot()))
        self.controller.task(IPS_NamedTask('Create metadata', self.create_metadata()))

        # Assign user defined .ips tasks in build order
        for user_task in ordered_tasks:
            self.controller.task(IPS_NamedTask(user_task, self.script_dict[user_task]))


    def source_unpack(self):
        path = os.path.join(self.env['SOURCES'],
                            os.path.basename(self.key_dict['source_url']))
        ext = {
               '.tar': '{0:s} xf {1:s} -C {2:s}'.format(self.tool['tar'], path, self.env['BUILD']),
               '.tar.gz': '{0:s} xfz {1:s} -C {2:s}'.format(self.tool['tar'], path, self.env['BUILD']),
               '.tar.bz2': '{0:s} xfj {1:s} -C {2:s}'.format(self.tool['tar'], path, self.env['BUILD']),
               '.tar.xz': '{0:s} xfJ {1:s} -C {2:s}'.format(self.tool['tar'], path, self.env['BUILD']),
               '.gz': self.tool['gunzip'],
               '.bz2': self.tool['bunzip'],
               '.zip': self.tool['unzip']
        }
        cmd = []
        for k, v in ext.items():
            if k in path:
                cmd = v.split()
                subprocess.check_output(cmd)
                break
        return [cmd]

    def create_buildroot(self):
        path = os.path.join(self.env['BUILDROOT'],
                            self.key_dict['name'] +
                            "-" +
                            self.key_dict['version'])
        if os.path.exists(path):
            os.remove(path)
        os.mkdir(path)
        return [path]

    def create_metadata(self):
        output = []
        meta_map = {
                     'pkg.fmri': self.key_dict['name'],
                     'pkg.description': self.key_dict['description'],
                     'pkg.summary': self.key_dict['summary'],
                     'variant.arch': self.key_dict['arch'],
                     'info.upstream_url': self.key_dict['upstream_url'],
                     'info.source_url': self.key_dict['source_url'],
                     'info.classification': self.key_dict['classification']
                     }
        template = file('metadata.tpl', 'r')
        for line in template.readlines():
            for k, v in meta_map.items():
                if k in line:
                    # pkg.fmri requires special attention to build the proper
                    # package name IPS wants
                    if k == 'pkg.fmri':
                        output.append(line.replace('{}',
                           self.key_dict['group'] +
                           "/" +
                           self.key_dict['name'] +
                           "@" +
                           self.key_dict['version'] +
                           "," +
                           self.key_dict['release']
                           ).strip('\n'))
                        continue
                    # The rest of the value replacements are rather simple
                    output.append(line.replace('{}', v).strip('\n'))
        return output

    def create_package_list(self):
        pass


    def show_summary(self):
        print("Summary of {0:s}".format(self.key_dict['name']))
        for k, v in sorted(self.key_dict.items()):
            print("+ {0:s}: {1:s}".format(k, v))




testfile = "test.ips"
build = IPS_Build(testfile)
#build.show_summary()
build.controller.do_tasks()
#build.source_unpack()

