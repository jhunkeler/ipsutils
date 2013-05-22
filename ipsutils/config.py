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

        expandable = []
        for line in file(ipsfile).readlines():
            parts = shlex.split(line)
            t = string.Template(parts)
            expandable.append(t)

        for key in key_dict:
            for line in file(ipsfile).readlines():
                parts = shlex.split(line)
                if key + ":" in parts:
                    key_dict[key] = parts[1]

        found_data = False
        code_section = ['%build', '%prep', '%install', '%transforms']

        for section in code_section:
            for line in file(ipsfile).readlines():
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

        self.key_dict = key_dict
        self.script_dict = script_dict
