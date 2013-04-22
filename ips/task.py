# class TaskController(list):
#     def __init__(self):
#         super(TaskController, self).__init__()
#         self._store = []
# 
#     def task(self, task):
#         super(TaskController, self).append(task)
# 
#     def do_tasks(self):
#         for task in super(TaskController, self).__iter__():
#             retval = task.run()
#             if not retval:
#                 exit(retval)
                
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
        #self.stack.reverse()
        for i in self.stack:
            i.run()

class NamedTask(object):
    def __init__(self, name, func, *args):
        self.name = name
        self.task = func
        self.task_args = args
        print("New task: {0:s} {1:s}".format(self.name, self.task))

    def run(self):
        print("Running task: {0:s}".format(self.name))
        status = self.task(self.task_args)
        return status

class InternalTask(NamedTask):
    pass