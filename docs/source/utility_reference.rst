Utility reference
=================

ipsbuild
--------

::

   ipsbuild.py [-h] [--version] [--verbose] [--lint] [spec [spec ...]]
   
   Build Solaris 11 packages from .ips spec files
   
   positional arguments:
     spec        An ipsutils spec file
   
   optional arguments:
     -h, --help  show this help message and exit
     --version   Show version information
     --verbose   Increased verbosity
     --lint      Enables deep packaging checks


ipsutils-newspec
----------------

::

   usage: ipsutils-newspec.py [-h] [spec [spec ...]]
   
   Generates a fresh .ips spec file
   
   positional arguments:
     spec        name of package(s)
   
   optional arguments:
   -h, --help  show this help message and exit


ipsutils-sanity
---------------

::

   usage: ipsutils-sanity.py [-h] pkgpath
   
   Installation viability checking
   
   positional arguments:
     pkgpath     Path to package (e.g ~/ipsbuild/PKGS/{PACKAGE})
   
   optional arguments:
   -h, --help  show this help message and exit


ipsbuild-setuptree
------------------

*No usage information*
