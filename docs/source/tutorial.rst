Tutorial
********

.. warning::

   Never build IPS packages as root!

Please review the `SPEC File Format <spec_file_format.html>`_ before continuing.


Creating an IPS package from scratch
====================================

In this tutorial we will create an IPS package from the ground up.  
We will build **ccache** (`<http://ccache.samba.org>`_),
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

OR

Download ccache directly with ``wget``::
   
   wget -P ~/ipsbuild/SOURCES http://samba.org/ftp/ccache/ccache-3.1.9.tar.bz2
   
.. note::

   ``wget`` may not installed by default.  To install it on Solaris 11 execute:
   ``pkg install wget``







