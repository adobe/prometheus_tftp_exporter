#! /usr/bin/env python
"""Setup file for creating packages."""

import os
# from setuptools import setup
from distutils.core import setup

setup(
    name="prometheus_tftp_exporter",
    version="0.0.1",
    author='Johan Elmerfjord',
    author_email='jelmerfj@adobe.com',
    packages=['tftp_exporter'],
    scripts=['bin/install.sh', 'bin/tftp_exporter'],
    url='https://git.corp.adobe.com/compute-services-team/techops-generic/tree/master/Techops_KickstartUtilityServer',
    license='Adobe Systems proprietary',
    long_description=open('README').read(),
    install_requires=[
        "prometheus_client>=0.0.11",
    ],
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
    ],
)
