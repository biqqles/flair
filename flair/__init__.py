"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
__version__ = 0.1
try:
    from ctypes import windll
    IS_WIN = True
    IS_ADMIN = bool(windll.advpack.IsNTAdmin(0, None))
except ImportError:
    IS_WIN = False
    IS_ADMIN = False
else:
    del windll

if not IS_ADMIN:
    raise ImportError('flair must be run as administrator')

from . import hook, augment, inspect
from .inspect.state import FreelancerState
from .inspect import events
