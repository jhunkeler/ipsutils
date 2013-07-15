Installation
************

Requirements
============

* Solaris >= 11.0
* Python == 2.7


Getting ipsutils
================

Clone ipsutils git repository
-----------------------------

::

   git clone http://bitbucket.org/jhunkeler/ipsutils.git
   cd ipsutils


Generate ipsutils build environment
-----------------------------------

::

   PYTHONPATH=. ./ipsbuild-setuptree.py


Create source distribution
--------------------------

::

   python2.7 setup.py build sdist


Copy resulting tarball to ipsutils build SOURCES directory
----------------------------------------------------------

::

   cp dist/ipsutils-VERSION.tar.gz ~/ipsutils/SOURCES


Build ipsutils
==============

::

   PYTHONPATH=. ./ipsbuild.py ipsbuild.ips


Publish ipsutils to your local repository
-----------------------------------------

::

   pkgsend publish \
      -s /your/repo \
      -d ~/ipsutils/PKGS/ipsutils-VERSION/root \
      ~/ipsutils/PKGS/ipsutils-VERSION/ipsutils-VERSION.res


Install ipsutils from your local repository
-------------------------------------------

::

   pkg install ipsutils

