"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from typing import Dict
import os

from flint.formats import ini
import ctypes
import win32api
import winreg


def get_active_account_name() -> str:
    """Returns the currently active account's code ("name") from the registry.
    Note that Freelancer reads the account from the registry at the time of server connect.
    """
    handle = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_DIR)
    return winreg.QueryValueEx(handle, 'MPAccountName')[0]


def virtual_key_to_name(vk) -> str:
    """Get the name of a key from its VK (virtual key) code."""
    scan_code = win32api.MapVirtualKey(vk, 0)
    # pywin32 doesn't include GetKeyNameTextW so we need to use windll
    name_buffer = ctypes.create_unicode_buffer(32)
    ctypes.windll.user32.GetKeyNameTextW((scan_code << 16 | 0 << 24 | 1 << 25), name_buffer, len(name_buffer))
    if not name_buffer.value:
        raise ValueError(f'Invalid virtual key: {vk}')
    return name_buffer.value.lower()


def get_user_keymap() -> Dict[str, str]:
    """Get Freelancer's current key map as defined in UserKeyMap.ini, in a format understood by the `keyboard`
    module."""
    key_map = ini.sections(USER_KEY_MAP, fold_values=False)['keycmd']

    result = {}  # nicknames to keyboard "hotkeys"

    for keycmd in key_map:
        # each "key" in the INI consists of exactly one VK code, and up to one modifier represented as a name
        nickname, key_combo = keycmd['nickname'][0], keycmd['key'][0]  # todo: only gets first to simply things
        vk, *modifier = str(key_combo).split(',')
        try:
            name = virtual_key_to_name(int(vk))
        except ValueError:
            continue

        formatted = name + '+' + modifier[0] if modifier else name  # form into a string keyboard can understand
        result[nickname] = formatted
    return result


REGISTRY_DIR = r'Software\Microsoft\Microsoft Games\Freelancer\1.0'
USER_KEY_MAP = os.path.expanduser(r'~\Documents\My Games\Freelancer\UserKeyMap.ini')
CHAT_MESSAGE_MAX_LENGTH = 140
