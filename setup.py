#!/usr/bin/env python
from setuptools import setup

from xplane import __version__


with open('README.rst') as fd:
    long_description = fd.read()


setup(
    name='snakes-on-a-plane',
    version=__version__,
    description='A set of tools for interfacing with X-Plane 10.',
    long_description=long_description,
    author='Tom Leese',
    author_email='inbox@tomleese.me.uk',
    url='https://github.com/tomleese/pyxplane',
    packages=['xplane'],
    install_requires=['Pint'],
    setup_requires=['Sphinx >=1.3', 'wheel'],
    entry_points={
        'console_scripts': [
            'xplane-show-values = xplane.cli.show_values:main'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ]
)
