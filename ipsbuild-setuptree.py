import os
import sys

home = None
try:
    if sys.platform == 'linux2' or sys.platform == 'darwin':
        home = os.path.normpath(os.environ['HOME'])
    elif sys.platform == 'win32':
        home = os.path.normpath(os.environ['USERPROFILE'])
except:
    Exception("Unsupported platform: {0:s}".format(sys.platform))

head = os.path.join(home, 'ipsbuild')
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
#    try:
    create_dir(head)
#    except:
#        print("{0:s} already exists, please remove it.".format(head))

    try:
        for d in tree:
            create_dir(os.path.join(head, d))
    except:
        pass

if __name__ == '__main__':
    main()
