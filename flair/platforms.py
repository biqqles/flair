"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from sys import platform

WIN32 = platform.startswith('win32')
LINUX = platform.startswith('linux')

if not WIN32 and not LINUX:
    raise NotImplementedError('This platform is not supported (yet)')
