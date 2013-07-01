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
* **description** - Full description of package
* **summary** - Brief description of package
* **classification** - opensolaris package classification format [1]_
* **arch** - Destined architecture of the package
* **license** - License of the package

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