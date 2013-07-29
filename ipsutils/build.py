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
from . import env, task, tasks
import os


class Build(env.Environment):
    def __init__(self, ipsfile, *args, **kwargs):
        """Enqueue's build tasks in the controller stack and fire's off the
        build procedure.
        """
        super(Build, self).__init__(ipsfile)
        self.ipsfile = ipsfile
        # Inherited members are used to populate package information
        # as well as build tasks        
        
        if 'options' in kwargs:
            self.options = kwargs['options']

        os.chdir(self.env['IPSBUILD'])
        # Create list of build tasks
        ordered_tasks = ['prep', 'build', 'install']
        self.controller = task.Controller()

        # Assign built-in IPS tasks
        self.controller.task(tasks.Unpack(cls=self))
        self.controller.task(tasks.Buildroot(cls=self))
        self.controller.task(tasks.Metadata(cls=self))

        # Assign user defined .ips tasks in build order
        for user_task in ordered_tasks:
            self.controller.task(tasks.Script(self.script_dict[user_task], name=user_task, cls=self))

        # Assign file manifest tasks
        self.controller.task(tasks.Manifest(cls=self))
        self.controller.task(tasks.Transmogrify(cls=self))
        self.controller.task(tasks.Dependencies(cls=self))
        if not self.options.nodepsolve:
            self.controller.task(tasks.Resolve_Dependencies(cls=self))
        self.controller.task(tasks.AlignPermissions(cls=self))
        if self.options.lint:
            self.controller.task(tasks.Lint(cls=self))
        self.controller.task(tasks.Package(cls=self))
        self.controller.task(tasks.Package(cls=self, spkg=True))

    
    def show_summary(self):
        print("Summary of {0:s}".format(self.key_dict['name']))
        for k, v in self.key_dict.items():
            if not v:
                continue
            print("+ {0:s}: {1:s}".format(k, v))
