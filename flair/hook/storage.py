"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import os
from typing import Dict, Tuple
import xml.etree.ElementTree

from flint.formats import ini

from .. import IS_WIN

if IS_WIN:
    import ctypes
    import win32api
    import winreg

REGISTRY_DIR = r'Software\Microsoft\Microsoft Games\Freelancer\1.0'
USER_KEY_MAP = os.path.expanduser(r'~\Documents\My Games\Freelancer\UserKeyMap.ini')
DSY_LAUNCHER_ACCOUNTS = os.path.expanduser(r'~\Documents\My Games\Discovery\launcheraccounts.xml')
DSY_DSACE = os.path.expanduser(r'~\Documents\My Games\Freelancer\DSAce.log')
CHAT_MESSAGE_MAX_LENGTH = 140


def get_active_account_name() -> str:
    """Returns the currently active account's code ("name") from the registry.
    Note that Freelancer reads the account from the registry at the time of server connect.
    """
    assert IS_WIN
    handle = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_DIR)
    return winreg.QueryValueEx(handle, 'MPAccountName')[0]


def virtual_key_to_name(vk) -> str:
    """Get the name of a key from its VK (virtual key) code."""
    assert IS_WIN
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
    assert IS_WIN
    key_map = ini.parse(USER_KEY_MAP, 'keycmd', fold_values=False)

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


def tail_chat_log():
    """(Discovery only)
    Get the last message recorded in DSAce.log"""
    file_length = os.stat(DSY_DSACE).st_size
    f = open(DSY_DSACE)
    f.seek(file_length - CHAT_MESSAGE_MAX_LENGTH)  # can't do nonzero end-relative seeks so do this instead
    tail = f.read()
    return tail.splitlines()[-1]


def get_launcher_accounts() -> Dict[str, Tuple[str, str]]:
    """(Discovery only)
    Parse launcheraccounts.xml to a dictionary of tuples of the form {code: (name, description)}."""
    root = xml.etree.ElementTree.parse(DSY_LAUNCHER_ACCOUNTS).getroot()
    return {a.get('code'): (a.text, a.get('description')) for a in root.findall('account')}
