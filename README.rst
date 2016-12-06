The Smart File System Synchronizer
==================================

Introduction
------------

**The Use Case**

Many a times we need to run code developed on Windows but we also need to run/test the code on a Linux system. This may be required because:

- The code has to be cross platform for e.g. a Java/Python package which should support both Windows and Linux systems.

- The code is only meant to run on Linux systems but the team is more comfortable developing on a Windows system.

In these cases we constantly need to **manually** copy even the smallest change to a Linux system where the change will be tested. Things becomes complicated when many small changes spanning many files need to be copied. This is where smart_sync comes to the rescue.

**What smart_sync does**

It constantly watches a specified directory for any file system changes like file/directory created/modified/moved/deleted and in response it will push the modified content to the target(usually a remote) directory. In summary smart_sync will make sure that the remote directory is an exact mirror of your development directory at all times.


Installation
------------
Currently only Linux based platforms are supported and you would require *Python3* to run it. Support for other platforms and Python2 to be added soon.

Steps::

    $ pip3 install git+https://github.com/rsjethani/smart_sync

Usage Scenario
--------------

Let's assume you are working on a project called **myproject** on your local machine say **local-dev** and you test new changes in a VM say **test-vm**. Also after testing your changes you would push/check-in your changes to **deployment-server**.

Step 1: start smart_sync on local-dev like::

    $ smart_sync path/to/project remote_user@test-vm:path/to/target

Step 2: Just keep making changes on local-dev and forget about manually making any modification/changes on test-vm. 
