"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.

 This file ensures all hook components are initialised.
"""
import sys

from . import input, window

if sys.platform.startswith('win32'):
    from . import process, storage
elif sys.platform.startswith('linux'):
    from . import process_linux as process, storage_linux as storage
    from . import vk_linux
