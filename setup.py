#!/usr/bin/env python

from setuptools import setup, find_packages
import os
from azure_storage import __version__

PACKAGE_DIR = os.path.abspath(os.path.dirname(__file__))
os.chdir(PACKAGE_DIR)


setup(
    name='django-azure-storage',
    version=__version__,
    url="https://github.com/Rediker-Software/django-azure-storage",
    author="Kevin Brown",
    author_email="kbrown@rediker.com",
    description="Django storage backends for Windows Azure blob storage.",
    license="MIT",
    packages=find_packages(exclude=["tests*", ]),
    include_package_data=True,
    install_requires=[
        'Django>=1.3',
        'azure-storage>=0.20.0,<0.30.0',
    ],
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)
