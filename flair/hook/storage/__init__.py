"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from typing import Dict

from flint.formats import ini

from ... import platforms

REGISTRY_DIR = r'Software\Microsoft\Microsoft Games\Freelancer\1.0'
USER_KEY_MAP = f'{platforms.HOME}/Documents/My Games/Freelancer/UserKeyMap.ini'
CHAT_MESSAGE_MAX_LENGTH = 140


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


if platforms.WIN32:
    from .win32 import get_active_account_name, virtual_key_to_name
elif platforms.LINUX:
    from .linux import get_active_account_name, virtual_key_to_name
