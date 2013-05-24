import os.path
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

#from __future__ import print_function
from . import env, task
from . import tpl
from . import packaging 
import stat
import os
import sys
import shutil
import subprocess
import string
import shlex
import tempfile


class Build(env.Environment):
    def __init__(self, ipsfile, *args, **kwargs):
        # Parent Config parses configuration data in .ips file
        # Inherited members are used to populate package information
        # as well as build tasks
        super(Build, self).__init__(ipsfile)
        
        if 'options' in kwargs:
            self.options = kwargs['options']

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
        self.controller.task(task.NamedTask('Create manifest', self.create_manifest))
        self.controller.task(task.NamedTask('Check transforms (mogrify)', self.manifest_mogrify))
        self.controller.task(task.NamedTask('Generate automatic dependency list', self.manifest_depends))
        self.controller.task(task.NamedTask('Resolve dependencies', self.manifest_depends_resolve))

    def exec_scripted_process(self, *p):
        shebang = "#!/bin/bash\n"
        fp_tempfile = tempfile.NamedTemporaryFile('w+', prefix='ipsutils_', suffix='.sh', delete=False)
        os.chdir(self.env_pkg['BUILD'])
        err = 0
        fp_tempfile.write(shebang)
        for args in p:
            for arg in args:
                if not arg:
                    continue
                for line in arg:
                    # Variable expansion occurs here.  Unfortunately, env_pkg is NOT available
                    # from within the configuration class
                    t = string.Template(string.join(line))
                    line = t.safe_substitute(self.env_pkg)
                    fp_tempfile.write(line + '\n')
                    if self.options.verbose:
                        print(">>> {0:s}".format(line))
        fp_tempfile.flush()
        os.chmod(fp_tempfile.name, 0755)
        script = [fp_tempfile.name]
        proc = subprocess.Popen(script, stdout=sys.stdout)
        err = proc.wait()
        fp_tempfile.close()
        
        os.chdir(self.env['IPSBUILD'])
        return err
    
    def source_unpack(self, *p):
        path = os.path.abspath(self.env_pkg['SOURCES'])
        if not os.path.exists(path):
            print("{0:s}: does not exist".format(path))
            return False
        if os.path.exists(self.env_pkg['BUILD']):
            shutil.rmtree(self.env_pkg['BUILD'])

        ext = {
               '.tar': '{0:s} xf {1:s} -C {2:s}'.format(self.tool['tar'], path, self.env['BUILD']),
               '.tar.gz': '{0:s} xfz {1:s} -C {2:s}'.format(self.tool['tar'], path, self.env['BUILD']),
               '.tar.bz2': '{0:s} xfj {1:s} -C {2:s}'.format(self.tool['tar'], path, self.env['BUILD']),
               '.tar.xz': '{0:s} xfJ {1:s} -C {2:s}'.format(self.tool['tar'], path, self.env['BUILD']),
               '.gz': self.tool['gunzip'], # not implemented
               '.bz2': self.tool['bunzip'], # not implemented
               '.zip': self.tool['unzip'] # not implemented
        }

        err = None
        for k, v in ext.items():
            if k in path:
                cmd = v.split()
                if self.options.verbose:
                    print(string.join(cmd))
                proc = subprocess.Popen(cmd)
                err = proc.wait()
                break
        return err

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
        # A common problem that needs solving.  What if you need to name your
        # package something else?  "repackage"
        if self.key_dict['repackage']:
            repackas = 'repackage'
        else:
            repackas = 'name'
            
        output = []
        meta_map = {
                     'pkg.fmri': self.key_dict['group'] + "/" +
                           self.key_dict[repackas] + "@" +
                           self.key_dict['version'] + "," +
                           self.key_dict['release'],
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
                    output.append(line.replace('{}', v))
        template.close()

        # Generate intial IPS metadata file in buildroot
        metadata = file(os.path.join(self.env_meta['FILES']), 'w+')
        for line in output:
            if self.options.verbose:
                print(">>> {0:s}".format(line))                        
            metadata.writelines(line)
        metadata.close()
        return True

    def create_manifest(self, *p):
        command_pkg = [self.tool['pkgsend'],
                           'generate',
                           self.env_pkg['BUILDPROTO']]
        command_pkgfmt = [self.tool['pkgfmt']]
        fp = file(self.env_meta['FILES'], 'a')
        proc_pkg = subprocess.Popen(command_pkg,
                                        stdout=subprocess.PIPE)
        proc_pkgfmt = subprocess.Popen(command_pkgfmt,
                                       stdin=proc_pkg.stdout,
                                       stdout=fp)
        output, err = proc_pkgfmt.communicate()
        fp.close()
        if self.options.verbose:
            if output:
                for line in output:
                    print(">>> {0:s}".format(line))
        return err

    def manifest_mogrify(self, *p):
        command_pkg = [self.tool['pkgmogrify'],
                       '-DARCH={0:s}'.format(self.key_dict['arch']),
                       self.env_meta['FILES'],
                       self.env_meta['TRANS']]
        command_pkgfmt = [self.tool['pkgfmt']]
        fp = file(self.env_meta['TRANS'], 'w+')
        # Write %transforms block into transmogrification file
        # Proper syntax required.
        for line in self.script_dict['transforms']:
            fp.writelines(string.join(line))
        fp.close()
        
        fp = file(self.env_meta['FILES_PASS2'], 'w+')
        proc_pkg = subprocess.Popen(command_pkg,
                                        stdout=subprocess.PIPE)
        proc_pkgfmt = subprocess.Popen(command_pkgfmt,
                                       stdin=proc_pkg.stdout,
                                       stdout=fp)
        output, err = proc_pkgfmt.communicate()
        fp.close()
        
        if self.options.verbose:
            if output:
                for line in output:
                    print(">>> {0:s}".format(line))
        return err

    def manifest_depends(self, *p):
        command_pkg = [self.tool['pkgdepend'],
                       'generate',
                       '-md',
                       self.env_pkg['BUILDPROTO'],
                       self.env_meta['FILES_PASS2']]
        command_pkgfmt = [self.tool['pkgfmt']]
        fp = file(self.env_meta['DEPENDS'], 'w+')
        proc_pkg = subprocess.Popen(command_pkg,
                                        stdout=subprocess.PIPE)
        proc_pkgfmt = subprocess.Popen(command_pkgfmt,
                                       stdin=proc_pkg.stdout,
                                       stdout=fp)
        output, err = proc_pkgfmt.communicate()
        fp.close()
        if self.options.verbose:
            if output:
                for line in output:
                    print(">>> {0:s}".format(line))
        return err

    def manifest_depends_resolve(self, *p):
        command_pkg = [self.tool['pkgdepend'],
                       'resolve',
                       '-m',
                       self.env_meta['DEPENDS']]
        proc_pkg = subprocess.Popen(command_pkg, stderr=subprocess.STDOUT)
        err = proc_pkg.wait()
        return err

    def show_summary(self):
        print("Summary of {0:s}".format(self.key_dict['name']))
        for k, v in sorted(self.key_dict.items()):
            print("+ {0:s}: {1:s}".format(k, v))
