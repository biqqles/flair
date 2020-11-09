"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from datetime import datetime
import os

from PIL import ImageGrab

from ..hook import window, input
from .. import platforms
from . import Augmentation


class Screenshot(Augmentation):
    """Adds proper screenshot functionality to the game."""
    HOTKEY = 'ctrl+prtscn' if platforms.WIN32 else 'ctrl+compose'
    screenshots_root_dir = os.path.expanduser('~/Documents/My Games/Freelancer/Screenshots')

    def load(self):
        os.makedirs(self.screenshots_root_dir, exist_ok=True)
        input.bind_hotkey(self.HOTKEY, self.take_screenshot)

    def unload(self):
        input.unbind_hotkey(self.HOTKEY, self.take_screenshot)

    def take_screenshot(self):
        """Take and save am auto-named screenshot"""
        character_name = self._state.name
        system_name = self._state.system
        date = datetime.now().strftime('%y-%m-%d %H.%M.%S')  # in practice only one screenshot can be taken per second
        directory_path = os.path.join(self.screenshots_root_dir, str(character_name))
        file_path = os.path.join(directory_path, f'{date} {system_name}.png')
        os.makedirs(directory_path, exist_ok=True)
        ImageGrab.grab(window.get_screen_coordinates()).save(file_path, 'PNG')
