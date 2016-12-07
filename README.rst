The Smart File System Synchronizer
==================================

Introduction
------------

**The Use Case**

Many a times we need to run code developed on Windows but we also need to run/test the code on a Linux system. This may be required because:

- The code has to be cross platform for e.g. a Java/Python package which should support both Windows and Linux systems.

- The code is only meant to run on Linux systems but the team is more comfortable developing on a Windows system.

- Even if the development and test systems have same platform we may have to use a separate test system due to software/hardware constraints on the developemnt system.

In these cases we constantly need to **manually** copy even the smallest change to a Linux system where the change will be tested. Things becomes complicated when many small changes spanning many files need to be copied. This is where smart_sync comes to the rescue.

**What smart_sync does**

It constantly watches a specified directory for any file system changes like
file/directory created/modified/moved/deleted and in response it will push the
changes to the target(usually a remote) directory. In summary smart_sync will
make sure that the remote directory is an exact mirror of your development
directory at all times. Currently smart_sync relies on the famous 'rsync' tool
to push changes.


Installation
------------
Currently smart_sync is only tested for Linux based platforms it requires
*Python3* to run. Support for other platforms and Python2 to be added soon.

Steps::

    $ pip3 install git+https://github.com/rsjethani/smart_sync

Usage Scenario
--------------

Let's assume you are working on a project called **myproject** on your local
machine and you test new changes in a VM say **test-vm**.

Step 1: start smart_sync on local-dev like::

    $ smart_sync path/to/project remote_user@test-vm:path/to/target

Step 2: Just keep making changes on local-dev and forget about manually
copying any modification/changes on test-vm.

**Excluding files/directories/patterns from copying to target**

For this you can use ``-e/--exclude`` option. This options takes a space
separated list of files or directories which you want to exclude from syncing
process.For example::

    $ smart_sync  path/to/project  remote_user@test-vm:path/to/target -e file 1 '*.pyc' dir1 ...
    
**Excluding by reading from a file**

You can also give a file as an argument ``-f/--exclude-from`` to smart_sync which contains
files/diretories/patterns to ignore. For example::

    $ smart_sync  path/to/project  remote_user@test-vm:path/to/target -f path/to/project/.gitignore
Now smart_sync will not track changes on files etc. specified in .gitingnore file.

**Do not allow extra files on destination**

By default the destination may contain extra files other than what comes
from source. If you do not want this then use ``-d/--delete`` option.
