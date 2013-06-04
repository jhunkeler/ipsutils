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

class Config(object):
    def __init__(self, ipsfile):
        super(Config, self).__init__()
        key_dict = {
                'name': '',
                'repackage': '',
                'version': '',
                'release': '',
                'maintainer': '',
                'group': '',
                'upstream_url': '',
                'source_url': '',
                'description': '',
                'summary': '',
                'classification': '',
                'arch': '',
                'license': ''
                }

        script_dict = {
                  'build': [],
                  'prep': [],
                  'install': [],
                  'transforms': [],
                  'files': []
                  }

        #Initial key_dict population with raw values taken from ips file
        for key in key_dict:
            for line in file(ipsfile).readlines():
                parts = shlex.split(line)
                if key + ":" in parts:
                    key_dict[key] = parts[1]

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
                    key_dict[key] = parts[1]

        found_data = False
        code_section = ['%build', '%prep', '%install', '%transforms']

        for section in code_section:
            for line in ipsfile_output:
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                parts = shlex.split(line)
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
