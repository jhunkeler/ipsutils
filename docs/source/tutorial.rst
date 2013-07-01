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

   Creating directory: /Users/jhunk/ipsbuild
   Creating directory: /Users/jhunk/ipsbuild/BUILDROOT
   Creating directory: /Users/jhunk/ipsbuild/BUILD
   Creating directory: /Users/jhunk/ipsbuild/SPECS
   Creating directory: /Users/jhunk/ipsbuild/SOURCES
   Creating directory: /Users/jhunk/ipsbuild/PKGS
   Creating directory: /Users/jhunk/ipsbuild/SPKGS


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

   # ipsutils-newspec ~/ipsutils/ccache.ips
   Generating '/home/user/ipsutils/ccache.ips' spec file

Contents of generated file::

   name: ccache
   repackage:
   version:
   release: 1
   group:
   summary: ""
   license:
   maintainer: ""
   upstream_url:
   source_url:
   arch:
   classification: ""
   description: ""
   
   
   %prep
   
   %end
   
   %build
   
   %end
   
   %install
   
   %end
   
   %transforms
   
   %end


What are these keywords you speak of?
-------------------------------------

Keywords in an ipsutils SPEC file refer to the data inserted into the *fmri* section of a package manifest.

name
~~~~

The ``name`` of the package should match the first part of the source package.
If source package is named ``ccache-x.y.z.tar.gz`` the ``name`` field should be set to ``ccache``.
In the case of Python, for example, they use a capital 'p' in the source package filename: ``Python-3.2.1.tar.gz``.

repackas
~~~~~~~~

To create an IPS package under a different name use the ``repackas`` keyword.  In this case, ``Python``
can be repackaged as ``python3`` and all subsequent modules (numpy, scipy, etc) can be repackaged as
``python3-[module]`` to make administration easier.

version
~~~~~~~

The version of the package is generally provided in the name of the source archive.

release
~~~~~~~

The ``release`` keyword allow you to apply patches to the IPS package without the need to change the version number.
For example, if a maintainer releases a bugfix, but it does not increment the version number, you may apply the
patch, increment the release number, and push the package to your repository.  Clients will then receive the latest 
bugfix without incrementing the package version.

group
~~~~~

``group`` defines a subclass of the IPS package classification system.

summary
~~~~~~~

``summary`` is a very brief description of the package's functional purpose.

license
~~~~~~~

The ``license`` describes the package's current license (e.g. ``GPL``, ``BSD``, ``MIT``, etc)

maintainer
~~~~~~~~~~

The package maintainer's full name and email.  Use the format: ``John Doe <john@example.com>``

upstream_url
~~~~~~~~~~~~

URL to the original source archive on the internet (or intranet).  Example, ``http://www.example.com/package-1.0.0.tar.gz``

source_url
~~~~~~~~~~

Although ``upstream_url`` can be in URL format, it is not a requirement.  Example, ``package-1.0.0.tar.gz`` or ``http://www.example.com/package-1.0.0.tar.gz``

arch
~~~~

There are only two architectures available:

- i386
- sparc

.. note:

   This keyword is mandatory.  There is no automatic architecture detection in IPS.
   
classification
~~~~~~~~~~~~~~

For a list of package classifications please refer to `this site <http://docs.oracle.com/cd/E26502_01/html/E21383/gentextid-3283.html#scrolltoc>`_.

description
~~~~~~~~~~~

A long detailed description of your package.


Filling in the blanks
=====================

yadda yadda