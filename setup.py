from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='smart_sync',

    version='0.1.0dev1',

    description='Automatic and Smart File System Syncing',

    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/rsjethani/smart_sync',

    # Author details
    author='Ravi Shekhar Jethani',
    author_email='rsjethani@gmail.com',

    # Choose your license
    license='MIT',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # packages = find_packages(),
    py_modules = ['smart_sync'],

    install_requires = ['watchdog >= 0.8.3'],

    entry_points = {
        'console_scripts': ['smart_sync=smart_sync:main']
    }
)
