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
import shlex
import string
import StringIO
import collections

class Config(object):
    def __init__(self, ipsfile=''):
        """SPEC file parsing engine.
        """
        super(Config, self).__init__()
        
        #Defines possible FMRI section keywords used by IPS
        key_dict = collections.OrderedDict()
        key_dict['name'] = ''
        key_dict['repackage'] = ''
        key_dict['version'] = ''
        key_dict['release'] = ''
        key_dict['group'] = ''
        key_dict['summary'] = ''
        key_dict['license'] = ''
        key_dict['maintainer'] = ''
        key_dict['upstream_url'] = ''
        key_dict['source_url'] = ''
        key_dict['arch'] = ''
        key_dict['classification'] = ''
        key_dict['description'] = ''
        key_dict['badpath'] = ''

        #Define valid build script sections in SPEC file
        script_dict = collections.OrderedDict()
        script_dict['prep'] =  []
        script_dict['build'] = []
        script_dict['install'] =  []
        script_dict['transforms'] =  []
        
        if not ipsfile:
            self.key_dict = key_dict
            self.script_dict = script_dict
            return

        #Initial key_dict population with raw values taken from ips file
        for key in key_dict:
            for line in file(ipsfile).readlines():
                parts = shlex.split(line)
                if key + ":" in parts:
                    key_dict[key] = line[line.find(':')+1:].lstrip(' ').rstrip('\n').rstrip(' ')

        #Drop using the original file in favor of a StringIO buffer
        #Because we need room to breathe without rewriting the file
        #every time we run a build... that's a no-go.
        ipsfile_input = StringIO.StringIO()
        for line in file(ipsfile).readlines():
            t = string.Template(line)
            new_line = t.safe_substitute(key_dict)
            ipsfile_input.writelines(new_line)

        #Turn our input buffer into an output buffer then ditch the original.
        ipsfile_output = StringIO.StringIO(ipsfile_input.getvalue()).readlines()
        ipsfile_input.close()

        # Populate key_dict with expanded values
        for key in key_dict:
            for line in ipsfile_output:
                parts = shlex.split(line)
                if key + ":" in parts:
                    key_dict[key] = line[line.find(':')+1:].lstrip(' ').rstrip('\n').rstrip(' ')
        
        #Parse user defined scripts by section and store them in script_dict
        found_data = False
        code_section = ['%build', '%prep', '%install', '%transforms']

        for section in code_section:
            for line in ipsfile_output:
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                parts = shlex.split(line, posix=False)
                if '%end' in parts:
                    found_data = False
                if section in parts:
                    found_data = True
                    continue
                if found_data:
                    script_dict[section.strip('%')].append(parts)

        #Assign completed dictionaries to global class scope
        self.key_dict = key_dict
        self.script_dict = script_dict
        if not self.check_keywords():
            exit(1)

    def _quote(self, s):
        return "'" + s.replace("'", "'\\''") + "'"

    def check_keywords(self):
        """Validate SPEC file's FMRI section
        """
        mandatory = ['arch', 'classification', 'description', 'group',
        'license', 'maintainer', 'name', 'release', 'source_url', 'summary',
        'version']
        #Get list of keys without data
        for k, v in sorted(self.key_dict.items()):
            if k in mandatory and not v:
                print("Mandatory keyword \'{}\' has no value".format(k))
                return False
        return True
