Installation
============

The following installation methods are provided:

* a self-contained executable generated using PyInstaller_


Installation as the Self-Contained Executable on Linux
------------------------------------------------------

|project_name| is distributed as a single executable packaged using PyInstaller_.
So all you have to do is to download the latest executable from the release page
|release_url| and copy it to a location of your choice, for example
:code:`/usr/local/bin`.

    $ wget https://github.com/seeraven/gitcache/releases/download/v1.0.25/gitcache_v1.0.25_Ubuntu22.04_amd64
    $ mv gitcache_v1.0.25_Ubuntu22.04_amd64 /usr/local/bin/gitcache
    $ chmod +x /usr/local/bin/gitcache
    $ ln -s /usr/local/bin/gitcache /usr/local/bin/git


.. _PyInstaller: http://www.pyinstaller.org/
