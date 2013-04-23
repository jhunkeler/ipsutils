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

from . import env, task
from pprint import pprint
import os
import shutil
import subprocess
import string
from . import tpl


class Build(env.Environment):
    def __init__(self, ipsfile):
        # Parent Config parses configuration data in .ips file
        # Inherited members are used to populate package information
        # as well as build tasks
        super(Build, self).__init__(ipsfile)

        os.chdir(self.env['IPSBUILD'])
        # Create list of build tasks
        ordered_tasks = ['prep', 'build', 'install']
        self.controller = task.TaskController()

        # Assign built-in IPS tasks
        self.controller.task(task.NamedTask('Extract source', self.source_unpack))
        self.controller.task(task.NamedTask('Create buildroot', self.create_buildroot))
        self.controller.task(task.NamedTask('Create metadata', self.create_metadata))

        # Assign user defined .ips tasks in build order
        for user_task in ordered_tasks:
            self.controller.task(task.NamedTask(user_task, self.exec_scripted_process, self.script_dict[user_task]))

        # Assign file manifest tasks
        self.controller.task(task.NamedTask('Create file list', self.create_manifest))
        self.controller.task(task.NamedTask('Create file list', self.manifest_mogrify))
        self.controller.task(task.NamedTask('Create file list', self.manifest_depends))
        self.controller.task(task.NamedTask('Create file list', self.manifest_depends_resolve))

    def exec_scripted_process(self, *p):
        """Execute script in .ips
        This function needs to be rewritten BAD
        
        p: tuple of function arguments
        """
        # All execution occurs from within the build directory.
        # This includes all installation-like tasks
        os.chdir(self.env_pkg['BUILD'])
        for t in map(list, p):
            for i in t:
                if not i:
                    continue
                for e in i:
                    # Variable expansion occurs here.  Unfortunately, env_pkg is NOT available
                    # from within the configuration class
                    t = string.Template(string.join(e))
                    e = t.safe_substitute(self.env_pkg)
                    print("+ {0:s}".format(e))
                    # Using "shell" is dangerous, but we're in the business of danger... right?
                    output = subprocess.check_output(e, shell=True)
                    if output:
                        print("+ {0:s}".format(output).rstrip('\n'))
        os.chdir(self.env['IPSBUILD'])
        return True

    def source_unpack(self, *p):
        path = os.path.relpath(self.env_pkg['SOURCES'], self.env['IPSBUILD'])
        if not os.path.exists(path):
            print("{0:s}: does not exist".format(path))
            return False

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
                print(string.join(cmd))
                subprocess.check_output(cmd)
                break
        return True

    def create_buildroot(self, *p):
        """Destroy/Create BUILDROOT per execution to keep the envrionment stable
        
        p: tuple of function arguments
        """
        # BUILDPROTO is a subdirectory of BUILDROOT/pkgname
        path = self.env_pkg['BUILDPROTO']
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, 0755)
        return True

    def create_metadata(self, *p):
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

        # Perform metadata template mapping and expansion
        template = file(tpl.metadata, 'r')
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
                           ))
                        continue
                    # The rest of the value replacements are rather simple
                    output.append(line.replace('{}', v))
        template.close()

        # Generate intial IPS metadata file in buildroot
        metadata = file(os.path.join(self.env_meta['METADATA']), 'w+')
        for line in output:
            metadata.writelines(line)
        print(metadata.name)
        metadata.close()
        return True

    def create_manifest(self, *p):
        command_pkg = [self.tool['pkgsend'],
                           'generate',
                           self.env_pkg['BUILDPROTO']]
        command_pkgfmt = [self.tool['pkgfmt']]
        proc_pkg = subprocess.Popen(command_pkg,
                                        stdout=subprocess.PIPE)
        proc_pkgfmt = subprocess.Popen(command_pkgfmt,
                                       stdin=proc_pkg.stdout,
                                       stdout=self.env_meta['FILES'])
        output, err = proc_pkgfmt.communicate()
        if output:
            for line in output:
                print(line.rstrip('\n'))
        if err != 0:
            return False
        return True

    def manifest_mogrify(self, *p):
        command_pkg = [self.tool['pkgmogrify'],
                       '-DARCH={0:s}'.format(self.key_dict['arch']),
                       self.env_meta['FILES'],
                       self.env_meta['METADATA']]
        command_pkgfmt = [self.tool['pkgfmt']]
        proc_pkg = subprocess.Popen(command_pkg,
                                        stdout=subprocess.PIPE)
        proc_pkgfmt = subprocess.Popen(command_pkgfmt,
                                       stdin=proc_pkg.stdout,
                                       stdout=self.env_meta['TRANS'])
        output, err = proc_pkgfmt.communicate()
        if output:
            for line in output:
                print(line.rstrip('\n'))
        if err != 0:
            return False
        return True

    def manifest_depends(self, *p):
        command_pkg = [self.tool['pkgdepend'],
                       'generate',
                       '-md',
                       self.env_pkg['BUILDPROTO'],
                       self.env_meta['TRANS']]
        command_pkgfmt = [self.tool['pkgfmt']]
        proc_pkg = subprocess.Popen(command_pkg,
                                        stdout=subprocess.PIPE)
        proc_pkgfmt = subprocess.Popen(command_pkgfmt,
                                       stdin=proc_pkg.stdout,
                                       stdout=self.env_meta['DEPENDS'])
        output, err = proc_pkgfmt.communicate()
        if output:
            for line in output:
                print(line.rstrip('\n'))
        if err != 0:
            return False
        return True

    def manifest_depends_resolve(self):
        command_pkg = [self.tool['pkgdepend'],
                       'resolve',
                       '-m',
                       self.env_meta['DEPENDS']]
        proc_pkg = subprocess.Popen(command_pkg)
        err = proc_pkg.wait()
        if err != 0:
            return False
        return True

    def show_summary(self):
        print("Summary of {0:s}".format(self.key_dict['name']))
        for k, v in sorted(self.key_dict.items()):
            print("+ {0:s}: {1:s}".format(k, v))
