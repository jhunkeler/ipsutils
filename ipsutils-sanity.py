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
from ipsutils import task
import argparse
import os
import tempfile
import shutil
import subprocess
import sys


class Stage1(task.Task):
    def __init__(self, *args, **kwargs):
        super(Stage1, self).__init__(self, *args, **kwargs)
        self.name = "Create local IPS repository"

    def _create_repo(self):
        command_pkg = [self.cls.tool['pkgrepo'],
                       'create',
                       self.cls.repo]
        proc_pkg = subprocess.Popen(command_pkg, stderr=subprocess.STDOUT)
        err = proc_pkg.wait()
        return err                

    def task(self):
        err = self._create_repo()
        return err

class Stage2(task.Task):
    def __init__(self, *args, **kwargs):
        super(Stage2, self).__init__(self, *args, **kwargs)
        self.name = "Add local repository to publisher"

    def _add_publisher(self):
        command_pkg = [self.cls.tool['pkgrepo'],
                       '-s',
                       self.cls.repo,
                       'add-publisher',
                       self.cls.pkg]
        proc_pkg = subprocess.Popen(command_pkg, stderr=subprocess.STDOUT)
        err = proc_pkg.wait()
        return err
    
    def task(self):
        err = self._add_publisher()
        return err    

class Stage3(task.Task):
    def __init__(self, *args, **kwargs):
        super(Stage3, self).__init__(self, *args, **kwargs)
        self.name = "Publish package to local repository"

    def _publish(self):
        command_pkg = [self.cls.tool['pkgsend'],
                       'publish',
                       '-d',
                       self.cls.root,
                       '-s',
                       self.cls.repo,
                       self.cls.manifest]
        proc_pkg = subprocess.Popen(command_pkg, stderr=subprocess.STDOUT)
        err = proc_pkg.wait()
        return err        

    def task(self):
        err = self._publish()
        return err
    
class Stage4(task.Task):
    def __init__(self, *args, **kwargs):
        super(Stage5, self).__init__(self, *args, **kwargs)
        self.name = "Package installation dry-run"

    def _dryrun(self):
        command_pkg = [self.cls.tool['pkg'],
                       'install',
                       '-n',
                       '-v',
                       '-g',
                       self.cls.repo,
                       self.cls.pkg]
        proc_pkg = subprocess.Popen(command_pkg, stderr=subprocess.STDOUT)
        err = proc_pkg.wait()
        return err
        
    def task(self):
        err = self._dryrun()
        return err



class Sanity(task.Controller):
    def __init__(self, path):
        """Verify a package will install without going through the insanity
        of using pkglint
        
        path = Path to package
        """
        super(Sanity, self).__init__()
        self.root = os.path.join(path, 'root')
        self.manifest = os.path.join(path, os.path.basename(path) + ".res")
        self.pkg = os.path.basename(path.split('-')[0])
        self.path = path
        self.repo = tempfile.mkdtemp(suffix='ipsutils')
        self.tool = {
            'pkg': 'pkg',
            'pkgsend': 'pkgsend',
            'pkgrepo': 'pkgrepo'    
            }
        
        # Add tasks
        self.task(Stage1(cls=self))
        self.task(Stage2(cls=self))
        self.task(Stage3(cls=self))
        self.task(Stage4(cls=self))
        
        # Run tasks
        self.do_tasks(atexit=self._remove_repo)
        
        # Remove all traces of being here
        self._remove_repo()
                
    def _remove_repo(self):
        if os.path.exists(self.repo):
            shutil.rmtree(self.repo)


parser = argparse.ArgumentParser(description='Installation viability checking')
parser.add_argument('pkgpath', action="store", help='Path to package (e.g ~/ipsbuild/PKGS/{PACKAGE})')
args = parser.parse_args()

if args.pkgpath:
    pkgpath = os.path.realpath(args.pkgpath)

if not os.path.exists(pkgpath):
    print("Package '{}' does not exist.")
    exit(1)

# Thanks to IPS for not having a userland solution for installing packages
# even as a DRY RUN... we need root before we can continue.
user = os.getuid()
if user != 0:
    print("Sorry, only root may execute this utility...".format(sys.argv[0]))
    exit(1)
    
sanity = Sanity(pkgpath)

