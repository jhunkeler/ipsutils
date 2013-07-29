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
from . import task
from . import tpl
from collections import OrderedDict
import grp
import os
import pwd
import string
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile


class Lint(task.Task):
    def __init__(self, *args, **kwargs):
        """Execute LINT engine.
        In order to facility continued use, a cache directory is created
        in the user's home directory to store pkglint manifests.  There is
        *nothing* fast about pkglint (even with the cache).
        """
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
        """Automatically resolve dependencies.
        Note: IPS does a poor job of parsing Python dependencies.
        """
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
        """Automatically determine package dependencies.
        Note: IPS does not do a very good job of this
        """
        super(Dependencies, self).__init__(self, *args, **kwargs)
        self.name = "Automatic dependencies"

    def task(self):
        command_pkg = [self.cls.tool['pkgdepend'],
                       'generate',
                       '-md',
                       self.cls.env_pkg['BUILDPROTO'],
                       self.cls.env_meta['STAGE1_PASS2']]
        fp = file(self.cls.env_meta['STAGE3'], 'w+')
        proc_pkg = subprocess.Popen(command_pkg, stdout=fp)
        err = proc_pkg.wait()
        fp.flush()
        fp.close()
        
        if vars(self.cls.options)['nodepsolve']:
            shutil.copy2(self.cls.env_meta['STAGE3'], \
                         self.cls.env_meta['STAGE4'])
            
        if err <= 1:
            err = 0
        return err


class Transmogrify(task.Task):
    def __init__(self, *args, **kwargs):
        """Using pkgmogrify's format in %transforms, a user may define
        specific file modifications on the package manifest

        For specification see:
            man pkgmogrify(1)
        """
        super(Transmogrify, self).__init__(self, *args, **kwargs)
        self.name = "Transmogrifying file manifest"

    def task(self):
        command_pkg = [self.cls.tool['pkgmogrify'],
                       '-DARCH={0:s}'.format(self.cls.key_dict['arch']),
                       self.cls.env_meta['STAGE1'],
                       self.cls.env_meta['STAGE2']]
        fp = file(self.cls.env_meta['STAGE2'], 'w+')
        # Write %transforms block into transmogrification file
        # Proper syntax required.
        for line in self.cls.script_dict['transforms']:
            fp.writelines(string.join(line))
            fp.writelines('\n')
        fp.flush()
        fp.close()

        fp = file(self.cls.env_meta['STAGE1_PASS2'], 'w+')
        proc_pkg = subprocess.Popen(command_pkg, stdout=fp)
        err = proc_pkg.wait()
        fp.close()
        return err


class Manifest(task.Task):
    def __init__(self, *args, **kwargs):
        """Automatic generation of initial file manifest.
        """
        super(Manifest, self).__init__(self, *args, **kwargs)
        self.name = "Generate file manifest"

    def task(self):
        command_pkg = [self.cls.tool['pkgsend'],
                           'generate',
                           self.cls.env_pkg['BUILDPROTO']]
        fp = file(self.cls.env_meta['STAGE1'], 'a')
        proc_pkg = subprocess.Popen(command_pkg, stdout=fp)
        err = proc_pkg.wait()
        fp.flush()
        fp.close()
        return err


class Unpack(task.Task):
    def __init__(self, *args, **kwargs):
        """ Automatically detect supported archives and extract them
        into the BUILD directory.
        """
        super(Unpack, self).__init__(self, *args, **kwargs)
        self.name = "Unpack source"
        self.extract_with = 'Built-in'
        
        #Order is IMPORTANT, extended extensions must precede single notation.
        self.extensions = OrderedDict()
        self.extensions['tar'] = ['.tar.bz2', '.tar.gz', '.tar']
        self.extensions['zip'] = ['.zip']

    def untar(self, src, dest):
        if not tarfile.is_tarfile(src):
            return False
        archive = tarfile.open(src)
        archive.extractall(dest)
        archive.close()
        return True

    def untar_fast(self, src, dest):
        """Sick of waiting?  Me too.
        """
        tell_tar = 'xf'
        if vars(self.cls.options)['verbose']:
            tell_tar += 'v'
        command = [ self.cls.tool['tar'], tell_tar, src, '-C', dest ]
        proc = subprocess.Popen(command, stdout=sys.stdout)
        err = proc.wait()
        
        if err != 0:
            return False
        return True

    def unzip(self, src, dest):
        if not zipfile.is_zipfile(src):
            return False
        archive = zipfile.ZipFile(src)
        archive.extractall(dest)
        return True

    def unzip_fast(self, src, dest):
        """Sick of waiting?  Me too.
        """
        command = [ self.cls.tool['unzip'], '-d', dest, src ]
        proc = subprocess.Popen(command)
        err = proc.wait()
        if err != 0:
            return False
        return True

    def detect(self, filename):
        delim = '.'
        ext_split = filename[filename.find(delim):]
        for fmt, exts in self.extensions.items():
            for ext in exts:
                if ext in ext_split:
                    return fmt, ext
        return '', ext_split

    def task(self):
        path = os.path.abspath(self.cls.env_pkg['SOURCES'])
        if not os.path.exists(path):
            print("{0:s}: does not exist".format(path))
            return False
        
        if os.path.exists(self.cls.env_pkg['BUILD']):
            shutil.rmtree(self.cls.env_pkg['BUILD'])

        if vars(self.cls.options)['fast']:
            # Force system-level source extraction
            self.untar = self.untar_fast
            self.unzip = self.unzip_fast
            self.extract_with = 'OS Provided'
        
        err = None
        fmt, ext = self.detect(path)
        print("Detected {} archive with extension {}".format(fmt, ext))
        print("Extraction method: {}".format(self.extract_with))
        
        if fmt not in self.extensions.keys():
            print("Unsupported archive: {}".format(ext))
            return 1
        if fmt == 'tar':
            self.untar(path, self.cls.env['BUILD'])
        elif fmt == 'zip':
            self.unzip(path, self.cls.env['BUILD'])
        
        return err


class Buildroot(task.Task):
    def __init__(self, *args, **kwargs):
        """Destroy/Create BUILDROOT per execution to keep the environment stable
        """
        super(Buildroot, self).__init__(self, *args, **kwargs)
        self.name = "Create build root"

    def task(self):
        path = self.cls.env_pkg['BUILDROOT']
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, 0755)
        return True


class Metadata(task.Task):
    def __init__(self, *args, **kwargs):
        """Generates FMRI data for the package based on values found in the
        user-defined SPEC file.
        """
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
        """Create a bash script per script directive block in the user-defined
        SPEC file.  Each script *should* have its own environment, just like
        a normal script, however bugs may still exist in the variable expansion
        system.
        """
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
            fp_tempfile.writelines('\n')
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
        """Due to the bizarre requirements of IPS, this class creates a
        directory containing the final package manifest and the complete
        buildroot.  The ability to create an archive will be added if there
        is a need.
        """
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

class AlignPermissions(task.Internal):
    def __init__(self, *args, **kwargs):
        """Reduces the need for manual transmogrification.
        IPS ability to generate a manifest that is compatible with itself is
        incredibly bad.  Permissions in a manifest never match the system's
        directory permissions.

        In order to fix the situation we reference the manifest permissions and
        the system permissions, then replace the incorrect lines with the
        proper values.
        """
        super(AlignPermissions, self).__init__(self, *args, **kwargs)
        self.name = "Automatic permission alignment"
        self.filename = self.cls.env_meta['STAGE4']

    def task(self):
        system_paths = []
        manifest_paths = []
        corrections = []

        line_number = 1
        print("Discovering directory entries in manifest...")
        for line in file(self.filename):
            if line.startswith('dir'):
                line = line.lstrip('dir')
                tokens = shlex.split(line)
                path = OrderedDict()
                for token in tokens:
                    s = token.split('=')
                    path[s[0]] = s[1]
                path['line'] = line_number
                if self.cls.options.verbose:
                    print("line {}: {}".format(path['line'], line.rstrip('\n')))
                manifest_paths.append(path)
            line_number += 1

        # Check manifest paths against the real system paths
        # Rewrite manifest with the proper system-level permissions to prevent
        # IPS from bombing when installing simple packages with slightly 
        # different permissions.
        print("Cross-referencing system paths...")
        for ref in manifest_paths:
            orig = ref['path']
            real = os.path.join('/', orig)
            try:
                si = os.stat(os.path.realpath(real))
                owner = pwd.getpwuid(si.st_uid).pw_name
                group = grp.getgrgid(si.st_gid).gr_name
                mode = si.st_mode & 0777
                replacement = 'dir group={} mode={} owner={} path={}'.format(group, oct(mode), owner, orig)
                corrections.append({ref['line']: replacement})
            except:
                # Tried to stat a path that does not exist.
                # If it doesn't exist, we don't care... IPS will not barf
                # on permissions it doesn't already know about.
                continue
            
        if not corrections:
            print("No permission changes necessary!")
            return True
        
        line_number = 1
        found = False
        print("Repairing permissions...")
        infile = file(self.filename, 'r')
        outfile = tempfile.NamedTemporaryFile(delete=True)

        for line in infile.readlines():
            for correction in corrections:
                for pos, key in correction.items():
                    if line_number == pos:
                        found = True
                        if self.cls.options.verbose:
                            print("line {}: {}".format(line_number, key))
                        outfile.write(key + '\n')
            if not found:
                outfile.writelines(line)
            else:
                found = False
            line_number += 1
        outfile.flush()

        infile.close()
        shutil.copyfile(outfile.name, self.filename)
        outfile.close()
