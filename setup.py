#! /usr/bin/env python
"""
Setup file for creating packages.


Copyright 2018 Adobe. All rights reserved.
This file is licensed to you under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License. You may obtain a copy
of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
OF ANY KIND, either express or implied. See the License for the specific language
governing permissions and limitations under the License.
"""

import os
# from setuptools import setup
from distutils.core import setup

setup(
    name="prometheus_tftp_exporter",
    version="0.1.0",
    author='Johan Elmerfjord',
    author_email='jelmerfj@adobe.com',
    packages=['tftp_exporter'],
    scripts=['bin/install.sh', 'bin/tftp_exporter'],
    url='https://git.corp.adobe.com/compute-services-team/techops-generic/tree/master/Techops_KickstartUtilityServer',
    license='Apache Software License 2.0',
    keywords='prometheus monitoring exporter tftp',
    long_description=open('README.md').read(),
    install_requires=[
        "prometheus_client>=0.0.11",
    ],
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: Apache Software License",
    ],
)
