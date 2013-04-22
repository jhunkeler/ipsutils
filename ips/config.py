import shlex
import string

class Config(object):
    def __init__(self, ipsfile):
        super(Config, self).__init__()
        key_dict = {
                'name': '',
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
        code_section = ['%build', '%prep', '%install']
    
        for section in code_section:
            for line in file(ipsfile).readlines():
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
                        