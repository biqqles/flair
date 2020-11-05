"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from typing import Dict
import os

from flint.formats import ini

from . import vk_linux


def get_active_account_name() -> str:
    """Returns the currently active account's code ("name") from the registry.
    Note that Freelancer reads the account from the registry at the time of server connect.
    """
    with open(USER_REGISTRY_FILE_PATH, 'r') as f:
        wine_reg = f.read()
    path = None

    wine_reg_path = REGISTRY_DIR.replace('\\', '\\\\')
    for line in wine_reg.splitlines():
        if path != wine_reg_path:
            if line.startswith('['):
                path = line.split(']')[0][1:]
        else:
            if line.startswith('\"MPAccountName\"='):
                return line.split('=')[1].replace('\"', '')


def virtual_key_to_name(vk) -> str:
    """Get the name of a key from its VK (virtual key) code."""
    try:
        return vk_linux.vk_keycodes[vk].split("_")[1].lower()
    except KeyError:
        raise ValueError(f'Invalid virtual key: {vk}')


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


def set_wine_prefix_path(path):
    for folder in os.listdir(os.path.join(path, 'drive_c/users/')):
        if folder != 'Public':
            user = folder
            break
    global USER_KEY_MAP
    USER_KEY_MAP = os.path.join(
        path,
        r'drive_c/users/',
        user,
        r'My Documents/My Games/Freelancer/UserKeyMap.ini',
    )
    global USER_REGISTRY_FILE_PATH
    USER_REGISTRY_FILE_PATH = os.path.join(path, 'user.reg')


USER_REGISTRY_FILE_PATH = ""
REGISTRY_DIR = r'Software\Microsoft\Microsoft Games\Freelancer\1.0'
USER_KEY_MAP = ""
CHAT_MESSAGE_MAX_LENGTH = 140
