"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from abc import ABC, abstractmethod
from typing import List

from ..inspect.state import FreelancerState


class Augmentation(ABC):
    """The base (abstract) class for a game client augmentation."""
    def __init__(self, state: FreelancerState):
        self._state = state

    @abstractmethod
    def load(self):
        """Run when an augmentation is "loaded" into the game client. Connect up the events you need to use and add any
        other setup here."""
        pass

    @abstractmethod
    def unload(self):
        """Run when an augmentation is "unloaded" from the game client. Disconnect any events used here."""
        pass

    @classmethod
    def load_all(cls, state: FreelancerState) -> List['Augmentation']:
        """Instantiate and load all subclasses of this class. Returns a list containing references to these instances.
        Keep a reference to this to avoid them being garbage collected."""
        # ensure built-in augmentations are interpreted
        from . import cli, clipboard, screenshot
        instances = [s(state) for s in cls.__subclasses__()]
        for a in instances:
            a.load()
        return instances
