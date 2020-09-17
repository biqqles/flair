"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
__version__ = 0.4

from . import hook, augment, inspect
from .inspect import events
from .inspect.state import FreelancerState

state: FreelancerState


def set_install_path(path: str):
    """Set the path to the Freelancer installation directory this hook should work with. Accessing `state` before
    this is executed will cause an `AttributeError`."""
    global state
    state = FreelancerState(path)
