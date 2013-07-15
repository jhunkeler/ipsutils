Publishing
==========

.. warning::

   IPS has no security measures in place to prevent others from pushing malicious
   packages upstream.  To combat this problem you will need to adhere to two 
   simple rules:

   1. A repository marked read-write *must not* be accessible from the internet.
   2. Packages may only be pushed by trusted systems (restricted by a firewall)
   
If you have not created a custom repository, please refer to Oracle's 
`pkgrepo <http://docs.oracle.com/cd/E23824_01/html/E21796/pkgrepo-1.html>`_
documentation and `this tutorial <http://www.scalingbits.com/solaris/ips/configuration>`_ 
before continuing.
   
Which repository do I want?
---------------------------

.. warning::
   
   *Never* commit custom packages to the standard ``solaris`` repository.  Doing 
   so may break the entire IPS backend and cause future package upgrades to 
   fail.

Executing ``pkg publisher`` will display a list of available repositories: ::
   
   PUBLISHER                   TYPE     STATUS P LOCATION
   solaris                     origin   online F http://localhost/solaris
   solarisstudio               origin   online F http://localhost/solarisstudio
   myrepo                      origin   online F http://localhost/myrepo:10000


In this case you will want to use:
``myrepo`` and its *LOCATION* ``http://localhost/myrepo:10000``


Sending
-------

Using ``pkgsend``, commit an ipsutils package to your custom IPS repository: ::

   cd ~/ipsutils/PKGS/mypackage
   pkgsend -g http://localhost/myrepo:10000 -d root mypackage.res

Alternatively, you may use absolute paths: ::
   
   pkgsend -g http://localhost/myrepo:10000 \
      -d ~/ipsutils/PKGS/mypackage/root \
      ~/ipsutils/PKGS/mypackage/mypackage.res
   
.. note::
   
   A repository's **read-only** flag must be set to **False** for HTTP/HTTPS
   transactions to be successfull.


Refresh
-------

Before your package will be available (via HTTP) the repository must be refreshed.
On the IPS repository server, execute: ::

   pkgrepo refresh -s /path/to/repository
   

Testing
-------

In order to test installing your package, you will need to become root.  
Despite IPS providing a ``--dry-run`` argument, it will still write to files in
located in ``/var/pkg``.

Method One
~~~~~~~~~~

As root, execute: ::

   ipsutils-sanity.py ~/ipsutils/PKGS/mypackage
   
.. note::
   
   This method does not require a remote repository.  It will create a local
   repository in ``/tmp`` then delete it when it finishes.  Good to use if you
   are afraid to clutter up your existing repository.

Method Two
~~~~~~~~~~

As root, execute: ::
   
   pkg install --dry-run mypackage
