Tutorial
********

.. warning::

   Never build IPS packages as root!

Please review the `SPEC File Format <spec_file_format.html>`_ before continuing.


Creating an IPS package from scratch
====================================

In this tutorial we will create an IPS package from the ground up.  
We will build ``ccache`` (`<http://ccache.samba.org>`_),
because of its lightweight code footprint, and easy installation
method.


Generate ipsutils build tree
----------------------------


ipsutils provides a script to automatically create your build environment::

   ipsbuild-setuptree.py

Example output::

   Creating directory: /home/acct/ipsbuild
   Creating directory: /home/acct/ipsbuild/BUILDROOT
   Creating directory: /home/acct/ipsbuild/BUILD
   Creating directory: /home/acct/ipsbuild/SPECS
   Creating directory: /home/acct/ipsbuild/SOURCES
   Creating directory: /home/acct/ipsbuild/PKGS
   Creating directory: /home/acct/ipsbuild/SPKGS


Download the source
-------------------
.. _here: http://ccache.samba.org/download.html

Get the latest version from here_.

**-OR-**

Download ``ccache`` directly with ``wget``::
   
   wget -P ~/ipsbuild/SOURCES http://samba.org/ftp/ccache/ccache-3.1.9.tar.bz2
   
.. note::

   ``wget`` may not installed by default.  
   To install it on Solaris 11 execute:
   ``pkg install wget``


Creating a SPEC file
--------------------

Writing an ipsutils SPEC file from scratch is a daunting task, 
much like when working with RPM SPEC files.  There is a utility, ``ipsutils-newspec`` 
available to help.  This creates all available keywords and directives so that you
may pick and choose which ones to fill out.

::

   # ipsutils-newspec ~/ipsutils/SPECS/ccache.ips
   Generating '/home/acct/ipsutils/SPECS/ccache.ips' spec file

Contents of generated file::

   name: ccache
   repackage:
   version:
   release: 1
   group:
   summary:
   license:
   maintainer:
   upstream_url:
   source_url:
   arch:
   classification:
   description:
   
   
   %prep
   
   %end
   
   %build
   
   %end
   
   %install
   
   %end
   
   %transforms
   
   %end

.. warning::
   
   Keywords with no values specified will cause ipsbuild to fail
   
.. warning::
   
   Keywords must contain a single space after the ':' character


Filling in the FMRI section
---------------------------

The FMRI section of your SPEC file should look something like the following: ::

   name: ccache
   version: 3.1.9
   release: 1
   group: developer
   summary: Cache system for GCC
   license: GPL
   maintainer: John Doe <john@example.com>
   upstream_url: http://samba.org/ftp/ccache/$name-$version.tar.bz2
   source_url: $name-$version.tar.bz2
   arch: i386
   classification: org.opensolaris.category.2008:Development/C
   description: ccache is a compiler cache. It speeds up recompilation by caching previous compilations.


Applying scripts
----------------

``ccache`` does not require any prep work to get running.  
In practice, if we had a critial patch to apply, or configuration files to
modify, we would do so in the ``%prep`` section.


Build section
~~~~~~~~~~~~~

::
   
   %build
   
   # Run autotools script
   ./configure --prefix=/usr
   
   # Build the package
   gmake -j2
   
   %end

Install section
~~~~~~~~~~~~~~~

::
   
   %install
   
   gmake install DESTDIR=$BUILDPROTO
   
   %end
   
.. warning::
   
   Files copied to $BUILDPROTO will be incorporated into your package manifest

   
Applying transforms
-------------------

IPS packing contains a bizarre technology named *transmogrification* that, in theory,
is a great idea.  The ability to transform file names, permissions, paths all in
a single albeit long convoluted string directive.

It is too cumbersome to modify a package manifest by hand every time you realize
there is something missing.  The ``%transforms`` section is **not** a shell script.
Any text written to this section (except ``#`` comments) will be written directly 
to the package manifest.

Care must be taken to ensure the tranforms syntax is properly written, because like 
most things in Oracle IPS, there is no error checking at runtime.  Error checking
appears to be at-the-time, which makes writing IPS packages (successfully) a very
difficult experience. 

Syntax: [1]_ 
``<transform {type} {{keyword}={value} ...} -> {action} {modifications...}>``

Example usage ::

   %transforms
   <transform dir path=opt$ -> edit group bin sys>
   %end
   
This will change the group ownership of ``/opt`` from ``bin`` to ``sys``.
However, ipsutils does this for you automatically, making these calls no longer necessary.

.. [1] Not confusing at all, right Oracle?


Putting it all together
-----------------------

Your completed SPEC file, if you have been following along, should look similar to
the following: ::

   name: ccache
   version: 3.1.9
   release: 1
   group: developer
   summary: Cache system for GCC
   license: GPL
   maintainer: John Doe <john@example.com>
   upstream_url: http://samba.org/ftp/ccache/$name-$version.tar.bz2
   source_url: $name-$version.tar.bz2
   arch: i386
   classification: org.opensolaris.category.2008:Development/C
   description: ccache is a compiler cache. It speeds up recompilation by caching previous compilations.
   
   %build
   
   # Run autotools script
   ./configure --prefix=/usr
   
   # Build the package
   gmake -j2
   
   %end
      
   %install
   
   gmake install DESTDIR=$BUILDPROTO
   
   %end


Building your package
---------------------

The simplest and fastest way to get started building your IPS package requires
nothing fancy.  Execute ipsbuild and watch your build take flight.

::

   ipsbuild ccache.ips

Example (truncated for brevity)::

   Summary of ccache
   + name: ccache
   + repackage: 
   + version: 3.1.9
   + release: 1
   + group: developer
   + summary: Cache system for GCC
   + license: GPL
   + maintainer: John Doe <john@example.com>
   + upstream_url: http://samba.org/ftp/ccache/ccache-3.1.9.tar.bz2
   + source_url: ccache-3.1.9.tar.bz2
   + arch: i386
   + classification: org.opensolaris.category.2008:Development/C
   + description: ccache is a compiler cache. It speeds up recompilation by caching previous compilations.
   + Running task: Unpack source
   Detected archive with extension: .tar.bz2
   + Running task: Create build root
   + Running task: Generate meta data
   + Running task: prep
   + Running task: build
   configure: Configuring ccache
   [...]
   configure: creating ./config.status
   config.status: creating Makefile
   config.status: creating config.h
   configure: now build ccache by running make
   gcc -g -O2 -Wall -W -DHAVE_CONFIG_H  -I. -I. -c -o main.o main.c
   gcc -g -O2 -Wall -W -DHAVE_CONFIG_H  -I. -I. -c -o ccache.o ccache.c
   gcc -g -O2 -Wall -W -DHAVE_CONFIG_H  -I. -I. -c -o mdfour.o mdfour.c
   gcc -g -O2 -Wall -W -DHAVE_CONFIG_H  -I. -I. -c -o hash.o hash.c
   gcc -g -O2 -Wall -W -DHAVE_CONFIG_H  -I. -I. -c -o execute.o execute.c
   gcc -g -O2 -Wall -W -DHAVE_CONFIG_H  -I. -I. -c -o util.o util.c
   [...]
   + Running task: install
   /usr/bin/ginstall -c -d /home/acct/ipsbuild/BUILDROOT/ccache-3.1.9/root/usr/bin
   /usr/bin/ginstall -c -m 755 ccache /home/acct/ipsbuild/BUILDROOT/ccache-3.1.9/root/usr/bin
   /usr/bin/ginstall -c -d /home/acct/ipsbuild/BUILDROOT/ccache-3.1.9/root/usr/share/man/man1
   /usr/bin/ginstall -c -m 644 ./ccache.1 /home/acct/ipsbuild/BUILDROOT/ccache-3.1.9/root/usr/share/man/man1/
   + Running task: Generate file manifest
   + Running task: Transmogrifying file manifest
   + Running task: Automatic dependencies
   + Running task: Dependency resolution
   > Running internal task: Automatic permission alignment
   Discovering directory entries in manifest...
   Cross-referencing system paths...
   Repairing permissions...
   + Running task: Generate package
   + Running task: Generate source package
   

Publishing
==========

.. note::
   
   If you have not setup a custom repository, please refer to Oracle's ``pkgrepo`` documentation
   before continuing.
   
Repository discovery
--------------------

TODO

Sending
-------

TODO

Verifying
---------
 
TODO