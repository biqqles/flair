"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import keyboard
import pyperclip

from . import Augmentation
from ..hook import input, process
from ..inspect.events import chat_box_opened, chat_box_closed


class Clipboard(Augmentation):
    """Adds clipboard functionality to the chat box."""
    HOTKEY_PASTE = 'ctrl+shift+v'
    HOTKEY_COPY = 'ctrl+shift+c'

    def load(self):
        chat_box_opened.connect(self.hook_copy)
        chat_box_opened.connect(self.hook_paste)
        chat_box_closed.disconnect(self.hook_copy)
        chat_box_closed.disconnect(self.hook_paste)

    def unload(self):
        chat_box_opened.disconnect(self.hook_copy)
        chat_box_opened.disconnect(self.hook_paste)

    @classmethod
    def hook_copy(cls):
        keyboard.add_hotkey(cls.HOTKEY_COPY, cls.copy_from_chat_box)

    @classmethod
    def hook_paste(cls):
        keyboard.add_hotkey(cls.HOTKEY_PASTE, cls.paste_to_chat_box)

    @staticmethod
    def copy_from_chat_box():
        assert process.get_chat_box_state(process.get_process())
        text = input.get_chat_box_contents()
        if text:  # if there's nothing in the chat box don't just wipe out what's currently in the clipboard
            pyperclip.copy(text)

    @staticmethod
    def paste_to_chat_box():
        assert process.get_chat_box_state(process.get_process())
        contents = pyperclip.paste()
        if contents:
            input.inject_text(contents.replace('\n', ''))
