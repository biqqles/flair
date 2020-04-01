"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from setuptools import setup

setup(
    name='fl-flair',
    version='0.1',
    author='biqqles',
    author_email='biqqles@protonmail.com',
    description='A novel client-side hook for Freelancer',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/biqqles/flair',
    packages=['flair', 'flair.augment', 'flair.hook', 'flair.inspect'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Games/Entertainment',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha'
    ],
    python_requires='>=3.6',
    install_requires=open('requirements.txt').readlines(),
)
