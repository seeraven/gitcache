Welcome to gitcache documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :name: mastertoc

   installation
   usage
   development


Introduction
------------

gitcache is a command line tool to manage boxes to provide a local cache for git
repositories to speed up working with large repositories and multiple clones.

The basic idea of gitcache is to act as a wrapper for the :code:`git` command and
use a local bare mirror as the repository source when cloning and pulling
repositories.


Requirements
------------

Depending on the type of distribution, gitcache has the following requirements:

* python3
* git
* git-lfs


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
