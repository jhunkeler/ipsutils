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

class TaskException(Exception):
    pass

class InternalTaskException(Exception):
    pass

class TaskControllerException(Exception):
    pass

class Controller(object):
    def __init__(self):
        """Simple FILO execution stack of task objects
        
        Example:
        from ipsutils import tasks
        
        #Create a new controller
        controller = task.Controller()
        #Add a tasks
        controller.task(task.Task(name='Some task'))
        controller.task(task.Task(name='Some other task'))
        #Execute tasks
        controller.do_tasks()
        
        Output:
        + Running task: Some task
        + Running task: Some other task
        """
        self.stack = []

    def task(self, t):
        """
        t: Task object
        """
        if not isinstance(t, Task):
            raise TaskControllerException("'{}' is not an instance of Task".format(type(t)))
        self.stack.append(t)

    def do_tasks(self, atexit=None):
        """ FILO execution of tasks
        """
        if not self.stack:
            raise TaskException("Empty controller stack")
        
        for stack_entry in self.stack:
            status = stack_entry.run()
            if type(status) == type(True):
                if not status:
                    print("Internal error: {}".format(status))
                    if atexit is not None:
                        atexit()
                    exit(status)
            else:
                if status is not 0 \
                and status is not None:
                    print("exit: {}".format(status))
                    if atexit is not None:
                        atexit()                    
                    exit(status)

class Task(object):
    def __init__(self, *args, **kwargs):
        """Task engine base class.
        
        Keyword arguments:
        name = Description of the task
        func = Function reference
        cls = An instance of the calling class (if any)
        
        """
        self.name = ''
        if 'name' in kwargs:
            self.name = kwargs['name']
        
        if 'func' in kwargs:
            self.func = kwargs['func']
        else:
            self.func = None
            
        if 'cls' in kwargs:
            self.cls = kwargs['cls']
            if not isinstance(self.cls, object):
                raise TaskException("'{}' is not an instance of a class".format(type(self.cls)))
        else:
            self.cls = object()
    
    def run(self):
        if not self.name:
            raise TaskException("Unnamed task in: {}".format(self.__class__.__name__))
        
        print("> Running task: {0:s}".format(self.name))
        status = self.task()
        return status
        
    def task(self):
        raise NotImplementedError('Task undefined')


class Internal(Task):
    def __init__(self, *args, **kwargs):
        """Implements an internal task denoted by a slightly different output.
        """
        super(Internal, self).__init__(self, *args, **kwargs)

    def run(self):
        if not self.name:
            raise InternalTaskException("Unnamed task in : {}".format(self.name))
        print("> Running internal task: {0:s}".format(self.name))
        status = self.task()
        return status
