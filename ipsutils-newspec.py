#!/usr/bin/env python
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
import argparse
import ipsutils
import os.path


parser = argparse.ArgumentParser(description='Generates a fresh .ips spec file')
parser.add_argument('spec', nargs='*', help='name of package(s)')
args = parser.parse_args()

if args.spec:
    for spec in args.spec:
        spec_template = ipsutils.config.Config()
        spec_template.key_dict['name'] = os.path.splitext(os.path.basename(spec))[0]
        spec_template.key_dict['release'] = '1'

        print("Generating '{}' spec file".format(os.path.basename(spec)))
        fp = file(spec, 'w+')
        for key, val in spec_template.key_dict.items():
            # Write non-essential keywords, commented
            if key is 'repackage' \
                or key is 'badpath':
                key = '#' + key
            # Write initial classification string (user needs to fill it in)
            if key is 'classification':
                val = 'org.opensolaris.category.2008:'
            if key is 'upstream_url':
                val = 'http://'
            fp.write('{}: {}\n'.format(key, val))
        fp.write('\n')

        for key in spec_template.script_dict.keys():
            fp.write('\n')
            fp.write('%{}\n\n'.format(key))
            fp.write('%end\n\n')
        fp.flush()
        fp.close()
else:
    print("For detailed usage information:\n\t--help or -h")
