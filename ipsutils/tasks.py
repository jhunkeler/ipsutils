from . import task
from . import tpl
import os
import string
import shutil
import subprocess
import sys
import tempfile


class Lint(task.Task):
    def __init__(self, *args, **kwargs):
        super(Lint, self).__init__(self, *args, **kwargs)
        self.name = "Package LINT checking (this may take a while...)"
        self.cachedir = os.path.join(os.environ['HOME'], '.ipscache')
        
    def _check_cache(self):
        if not os.path.exists(self.cachedir):
            print("Creating cache directory: {0:s}".format(self.cachedir))
            os.mkdir(self.cachedir)
            return False
        return True
            
    def _create_cache(self):
        command_pkg = [self.cls.tool['pkglint'],
                       '-c',
                       self.cachedir,
                       '-r',
                       'http://pkg.oracle.com/solaris/release/',
                       self.cls.env_meta['STAGE4']]
        print("Creating cache (this may take a while...)")
        proc_pkg = subprocess.Popen(command_pkg, stderr=subprocess.STDOUT)  
        err = proc_pkg.wait()
        return err
        
    def task(self):
        if not self._check_cache():
            self._create_cache()
            
        command_pkg = [self.cls.tool['pkglint'],
                       '-c',
                       self.cachedir,
                       self.cls.env_meta['STAGE4']]
        proc_pkg = subprocess.Popen(command_pkg, stderr=subprocess.STDOUT)
        err = proc_pkg.wait()
        return err
    
    
class Resolve_Dependencies(task.Task):
    def __init__(self, *args, **kwargs):
        super(Resolve_Dependencies, self).__init__(self, *args, **kwargs)
        self.name = "Dependency resolution"
        
    def task(self):
        command_pkg = [self.cls.tool['pkgdepend'],
                       'resolve',
                       '-m',
                       self.cls.env_meta['STAGE3']]
        proc_pkg = subprocess.Popen(command_pkg, stderr=subprocess.STDOUT)
        err = proc_pkg.wait()
        return err


class Dependencies(task.Task):
    def __init__(self, *args, **kwargs):
        super(Dependencies, self).__init__(self, *args, **kwargs)
        self.name = "Automatic dependencies"

    def task(self):
        command_pkg = [self.cls.tool['pkgdepend'],
                       'generate',
                       '-md',
                       self.cls.env_pkg['BUILDPROTO'],
                       self.cls.env_meta['STAGE1_PASS2']]
        command_pkgfmt = [self.cls.tool['pkgfmt']]
        fp = file(self.cls.env_meta['STAGE3'], 'w+')
        proc_pkg = subprocess.Popen(command_pkg,
                                        stdout=subprocess.PIPE)
        proc_pkgfmt = subprocess.Popen(command_pkgfmt,
                                       stdin=proc_pkg.stdout,
                                       stdout=fp)
        output, err = proc_pkgfmt.communicate()
        fp.close()
        if self.cls.options.verbose:
            if output:
                for line in output:
                    print(">>> {0:s}".format(line))
        return err


class Transmogrify(task.Task):
    def __init__(self, *args, **kwargs):
        super(Transmogrify, self).__init__(self, *args, **kwargs)
        self.name = "Transmogrifying file manifest"

    def task(self):
        command_pkg = [self.cls.tool['pkgmogrify'],
                       '-DARCH={0:s}'.format(self.cls.key_dict['arch']),
                       self.cls.env_meta['STAGE1'],
                       self.cls.env_meta['STAGE2']]
        command_pkgfmt = [self.cls.tool['pkgfmt']]
        fp = file(self.cls.env_meta['STAGE2'], 'w+')
        # Write %transforms block into transmogrification file
        # Proper syntax required.
        for line in self.cls.script_dict['transforms']:
            fp.writelines(string.join(line))
        fp.close()
        
        fp = file(self.cls.env_meta['STAGE1_PASS2'], 'w+')
        proc_pkg = subprocess.Popen(command_pkg,
                                        stdout=subprocess.PIPE)
        proc_pkgfmt = subprocess.Popen(command_pkgfmt,
                                       stdin=proc_pkg.stdout,
                                       stdout=fp)
        output, err = proc_pkgfmt.communicate()
        fp.close()
        
        if self.cls.options.verbose:
            if output:
                for line in output:
                    print(">>> {0:s}".format(line))
        return err


class Manifest(task.Task):
    def __init__(self, *args, **kwargs):
        super(Manifest, self).__init__(self, *args, **kwargs)
        self.name = "Generate file manifest"
        
    def task(self):
        command_pkg = [self.cls.tool['pkgsend'],
                           'generate',
                           self.cls.env_pkg['BUILDPROTO']]
        command_pkgfmt = [self.cls.tool['pkgfmt']]
        fp = file(self.cls.env_meta['STAGE1'], 'a')
        proc_pkg = subprocess.Popen(command_pkg,
                                        stdout=subprocess.PIPE)
        proc_pkgfmt = subprocess.Popen(command_pkgfmt,
                                       stdin=proc_pkg.stdout,
                                       stdout=fp)
        output, err = proc_pkgfmt.communicate()
        fp.close()
        if self.cls.options.verbose:
            if output:
                for line in output:
                    print(">>> {0:s}".format(line))
        return err


class Unpack(task.Task):
    def __init__(self, *args, **kwargs):
        super(Unpack, self).__init__(self, *args, **kwargs)
        self.name = "Unpack source"
        
    def task(self):
        path = os.path.abspath(self.cls.env_pkg['SOURCES'])
        if not os.path.exists(path):
            print("{0:s}: does not exist".format(path))
            return False
        if os.path.exists(self.cls.env_pkg['BUILD']):
            shutil.rmtree(self.cls.env_pkg['BUILD'])

        ext = {
               '.tar': '{0:s} xf {1:s} -C {2:s}'.format(self.cls.tool['tar'], path, self.cls.env['BUILD']),
               '.tar.gz': '{0:s} xfz {1:s} -C {2:s}'.format(self.cls.tool['tar'], path, self.cls.env['BUILD']),
               '.tar.bz2': '{0:s} xfj {1:s} -C {2:s}'.format(self.cls.tool['tar'], path, self.cls.env['BUILD']),
               '.tar.xz': '{0:s} xfJ {1:s} -C {2:s}'.format(self.cls.tool['tar'], path, self.cls.env['BUILD']),
               '.gz': self.cls.tool['gunzip'], # not implemented
               '.bz2': self.cls.tool['bunzip'], # not implemented
               '.zip': self.cls.tool['unzip'] # not implemented
        }

        err = None
        for k, v in ext.items():
            if k in path:
                cmd = v.split()
                if self.cls.options.verbose:
                    print(string.join(cmd))
                proc = subprocess.Popen(cmd)
                err = proc.wait()
                break
        return err


class Buildroot(task.Task):
    def __init__(self, *args, **kwargs):
        super(Buildroot, self).__init__(self, *args, **kwargs)
        self.name = "Create build root"
        
    def task(self):
        """Destroy/Create BUILDROOT per execution to keep the environment stable
        
        p: tuple of function arguments
        """
        path = self.cls.env_pkg['BUILDROOT']
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, 0755)
        return True


class Metadata(task.Task):
    def __init__(self, *args, **kwargs):
        super(Metadata, self).__init__(self, *args, **kwargs)
        self.name = "Generate meta data"
        
    def task(self):
        # A common problem that needs solving.  What if you need to name your
        # package something else?  "repackage"
        if self.cls.key_dict['repackage']:
            repackas = 'repackage'
        else:
            repackas = 'name'
            
        output = []
        meta_map = {
                     'pkg.fmri': self.cls.key_dict['group'] + "/" +
                           self.cls.key_dict[repackas] + "@" +
                           self.cls.key_dict['version'] + "," +
                           self.cls.key_dict['release'],
                     'pkg.description': self.cls.key_dict['description'],
                     'pkg.summary': self.cls.key_dict['summary'],
                     'variant.arch': self.cls.key_dict['arch'],
                     'info.upstream_url': self.cls.key_dict['upstream_url'],
                     'info.source_url': self.cls.key_dict['source_url'],
                     'info.classification': self.cls.key_dict['classification']
                     }

        # Perform metadata template mapping and expansion
        template = file(tpl.metadata, 'r')
        for line in template.readlines():
            for k, v in meta_map.items():
                if k in line:
                    output.append(line.replace('{}', v))
        template.close()

        # Generate intial IPS metadata file in buildroot
        metadata = file(os.path.join(self.cls.env_meta['STAGE1']), 'w+')
        for line in output:
            if self.cls.options.verbose:
                print(">>> {0:s}".format(line))                        
            metadata.writelines(line)
        metadata.close()
        return True


class Script(task.Task):
    def __init__(self, script, *args, **kwargs):
        super(Script, self).__init__(self, *args, **kwargs)
        self.script = script
        
    def task(self):
        shebang = "#!/bin/bash\n"
        fp_tempfile = tempfile.NamedTemporaryFile('w+', prefix='ipsutils_', suffix='.sh', delete=True)
        os.chdir(self.cls.env_pkg['BUILD'])
        fp_tempfile.write(shebang)
        for line in self.script:
            if not line:
                continue
            # Variable expansion occurs here.  Unfortunately, env_pkg is NOT available
            # from within the configuration class
            t = string.Template(string.join(line))
            line = t.safe_substitute(self.cls.env_pkg)
            fp_tempfile.writelines(line)
            if self.cls.options.verbose:
                print(">>> {0:s}".format(line))
        fp_tempfile.flush()
        os.chmod(fp_tempfile.name, 0755)
        script = [fp_tempfile.name]
        proc = subprocess.Popen(script, stdout=sys.stdout)
        err = proc.wait()
        fp_tempfile.close()
        
        os.chdir(self.cls.env['IPSBUILD'])
        return err


class Package(task.Task):
    def __init__(self, *args, **kwargs):
        super(Package, self).__init__(self, *args, **kwargs)
        self.name = "Generate package"        
        self.spkg = False
        self.source = self.cls.env_pkg['BUILDROOT']
        self.destination = self.cls.env_pkg['PKGS']
        if 'spkg' in kwargs:
            self.spkg = True
            self.name = "Generate source package"
            self.destination = self.cls.env_pkg['SPKGS']
    
    def task(self):
        if os.path.exists(self.destination):
            shutil.rmtree(self.destination)
        
        if self.spkg:
            os.mkdir(self.destination)
            shutil.copy2(self.cls.ipsfile, self.destination)
            shutil.copy2(self.cls.env_pkg['SOURCES'], self.destination)
        else:
            shutil.copytree(self.cls.env_pkg['BUILDPROTO'], \
                            os.path.join(self.destination, \
                            os.path.basename(self.cls.env_pkg['BUILDPROTO'])))
            shutil.copy2(self.cls.env_meta['STAGE4'], self.destination)
        
        return 0    

