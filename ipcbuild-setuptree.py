import os
import sys

try:
    if sys.platform == 'linux' or sys.platform == 'darwin':
        home = os.path.normpath(os.environ['HOME'])
    elif sys.platform == 'win32':
        home = os.path.normpath(os.environ['USERPROFILE'])
except:
    Exception("Unsupported platform: {0:s}".format(sys.platform))
    
head = os.path.join(home, 'ipcbuild')
tree = ['BUILDROOT',
        'BUILD',
        'SPECS',
        'SOURCES',
        'PKGS',
        'SPKGS']

def create_dir(dirent):
    print("Creating directory: {0:s}".format(dirent))
    os.mkdir(dirent)

def main():
    try:
        self.create_dir(head)
    except:
        print("{0:s} already exists, please remove it.".format(head))
    
    try:
        for d in tree:
            self.create_dir(os.path.join(head, d))
    except:
        pass

if __name__ == '__main__':
    main()