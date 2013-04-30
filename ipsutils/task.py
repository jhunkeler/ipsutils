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

class TaskController(object):
    def __init__(self):
        self.stack = []

    def task(self, t):
        """
        t: Task object
        """
        self.stack.append(t)

    def do_tasks(self):
        """ FILO execution of tasks
        """
        for stack_entry in self.stack:
            status = stack_entry.run()
            if not status:
                print("Exiting...")
                exit(status)


class NamedTask(object):
    def __init__(self, name, func, *args):
        self.name = name
        self.task = func
        self.task_args = args

    def run(self):
        print("Running task: {0:s}".format(self.name))
        status = self.task(self.task_args)
        return status

class InternalTask(NamedTask):
    pass
