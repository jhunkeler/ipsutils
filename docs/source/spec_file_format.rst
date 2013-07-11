SPEC File Format
****************

Keywords
========

* **name** - The name of the package
* **repackage** - Change name of package
* **version** - Version of package
* **release** - Release number of package
* **maintainer** - Name and email address of current package maintainer

* **group** - Name of group the package belongs to
* **upstream_url** - URL to package in repository
* **source_url** - URL to original source package
* **badpath** - Name of extracted top-level directory
* **description** - Full description of package
* **summary** - Brief description of package
* **classification** - opensolaris package classification format [1]_
* **arch** - Destined architecture of the package
* **license** - License of the package

Keywords, in-depth
==================

.. _FMRI: http://docs.oracle.com/cd/E26502_01/html/E21383/pkgterms.html#glubk

Keywords in an ipsutils SPEC file refer to the data inserted into the FMRI_ section of a package manifest.

name
----

The ``name`` of the package should match the first part of the source package.
If source package is named ``ccache-x.y.z.tar.gz`` the ``name`` field should be set to ``ccache``.
In the case of Python, for example, they use a capital 'p' in the source package filename: ``Python-3.2.1.tar.gz``.

repackas
--------

To create an IPS package under a different name use the ``repackas`` keyword.  In this case, ``Python``
can be repackaged as ``python3`` and all subsequent modules (numpy, scipy, etc) can be repackaged as
``python3-[module]`` to make administration easier.

version
-------

The version of the package is generally provided in the name of the source archive.

release
-------

The ``release`` keyword allow you to apply patches to the IPS package without the need to change the version number.
For example, if a maintainer releases a bugfix, but it does not increment the version number, you may apply the
patch, increment the release number, and push the package to your repository.  Clients will then receive the latest 
bugfix without incrementing the package version.

group
-----

``group`` defines a subclass of the IPS package classification system.

summary
-------

``summary`` is a very brief description of the package's functional purpose.

license
-------

The ``license`` describes the package's current license (e.g. ``GPL``, ``BSD``, ``MIT``, etc)

maintainer
----------

The package maintainer's full name and email.  Use the format: ``John Doe <john@example.com>``

upstream_url
------------

URL to the original source archive on the internet (or intranet).  Example, ``http://www.example.com/package-1.0.0.tar.gz``

source_url
----------

Although ``upstream_url`` can be in URL format, it is not a requirement.  Example, ``package-1.0.0.tar.gz`` or ``http://www.example.com/package-1.0.0.tar.gz``

badpath
-------
  
Some developers may package their source code with a top-level directory name that differs
from what is written to disk.

Example: ``gtar tfvz tkdiff-4.2.tar.gz`` ::

   -rw-r--r-- dorothyr/users 5910 2011-11-26 21:08 tkdiff-unix/CHANGELOG.txt
   -rw-r--r-- dorothyr/users 18092 2011-11-26 21:08 tkdiff-unix/LICENSE.txt
   -rwxr-xr-x dorothyr/users  1084 2011-11-26 21:08 tkdiff-unix/README.txt
   -rwxr-xr-x dorothyr/users 341372 2011-11-26 21:08 tkdiff-unix/tkdiff
   
The *name* of the package is **tkdiff-4.2** and the directory structure is **tkdiff-unix**.
This scenario will cause ipsbuild to fail unless the ``badpath`` keyword is used to circumvent the issue.

Example: ::

   badpath: tkdiff-unix

arch
----

There are only two architectures available:

- i386
- sparc

.. note:

   There is no automatic architecture detection in IPS.
   
classification
--------------

.. _classification: http://docs.oracle.com/cd/E26502_01/html/E21383/gentextid-3283.html#scrolltoc

For a list of package classifications please refer to the IPS package classification_ documentation.

description
-----------

A long detailed description of your package.


Directives
==========

.. note::
   All commands issued in a directive block are processed by Bourne-Again Shell,
   except for *%transforms*

.. note::
   Directives must be closed with the **%end** tag

%prep
-----

Set of commands to be executed *before building*;
such as applying patches to source code in the $BUILD directory, changing
pre-configuration data, etc.

Example::

   %prep
   # Apply various patches
   patch -i $SOURCES/$name-$version-some_fixes.patch
   
   # Change execution path of all scripts
   find $BUILD -type f -name "*.py" -exec sed -i -e 's|\!#/usr/local|\!#/usr/bin|g' {} \;
   
   %end

%build
------

Set of commands to be executed as part of the build process;
such as running any configuration scripts, and compiling your application(s).

Example::

   %build
   ./configure --prefix=/opt --with-pymalloc
   make -j2
   
   %end

%install
--------

Set of commands to executed as part of the installation process;
such as moving data to the build installation directory after being compiled.

Example::

   %install
   make install DESTDIR=$BUILDPROTO
   %end


%transforms
-----------

A syntatical reference is available from `oracle's transforms documentation <http://docs.oracle.com/cd/E26502_01/html/E21383/xformrules.html>`_

.. note::

   ``ipsbuild`` will automatically transmogrify directory permissions that do not match overlapping system directories.


Available shell expansion variables
===================================

* **BUILDROOT** - ipsutils/BUILDROOT/[package]
* **BUILDPROTO** - ipsutils/BUILDROOT/[package]/root
* **BUILD** - ipsutils/BUILD/[package]
* **SOURCES** - ipsutils/SOURCES/[package source_url basename]
* **PKGS** - ipsutils/PKGS/[package]
* **SPKGS** - ipsutils/SPKGS/[package]

.. note::
   All available *keywords* are expandable, too. 

.. note::
   Macro expansion for ipsutils is in its infancy.  If you are familiar with macro expansion
   in RPM's SPEC implementation; there is nothing even remotely close to it here.  This will be
   addressed in the future.

SPEC file example
=================

This is a generic example of an IPS spec file

::

   name:           ipsutils
   version:        0.6.0
   release:        1
   maintainer:     "Joseph Hunkeler <jhunk@stsci.edu>"
   upstream_url:   http://localhost/$name-$version.tar.gz
   source_url:     http://localhost/$name-$version.tar.gz
   description:    "Python IPS library"
   summary:        "A python based IPS library"
   group:          developer
   classification: "org.opensolaris.category.2008:Development/Distribution Tools"
   arch:           i386
   license:        GPL
   
   %prep
   %end
   
   %build
   python setup.py build
   
   %end
   
   %install
   python setup.py install --root=$BUILDPROTO --prefix=/opt/ipsutils
   %end
   
   %transforms
   <transform dir path=opt$ -> edit group bin sys>
   %end

   
Footnotes
=========

.. [1] `IPS package classifications <http://docs.oracle.com/cd/E26502_01/html/E21383/gentextid-3283.html#scrolltoc>`_