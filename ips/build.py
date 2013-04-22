from . import env, task
from pprint import pprint
import os
import shutil
import subprocess
import string


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

    def exec_scripted_process(self, *p):
        """Execute script in .ips
        This function needs to be rewritten BAD
        """
        os.chdir(self.env_pkg['BUILD'])
        for t in map(list, p):
            for i in t:
                if not i:
                    continue
                for e in i:
                    t = string.Template(string.join(e))
                    e = t.safe_substitute(self.env_pkg)
                    print("+ {0:s}".format(e))
                    output = subprocess.check_output(e)
                    if output:
                        print("+ {0:s}".format(output))
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
        path = self.env_pkg['BUILDROOT']
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
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
        template = file('c:\\users\\jhunk\\documents\\projects\\aptana\\ipsbuild\\metadata.tpl', 'r')
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
        
        manifest = file(os.path.join(self.env_pkg['BUILDROOT'], self.complete_name + '.p5m.1'), 'w+')
        for line in output:
            manifest.writelines(line)
        print(manifest.name)
        manifest.close()
        return True

    def create_package_list(self, *p):
        pass


    def show_summary(self):
        print("Summary of {0:s}".format(self.key_dict['name']))
        for k, v in sorted(self.key_dict.items()):
            print("+ {0:s}: {1:s}".format(k, v))
