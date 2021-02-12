"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from typing import Dict
import warnings

from flint.formats import ini
from flint.paths import construct_path

from ... import platforms

REGISTRY_DIR = r'Software\Microsoft\Microsoft Games\Freelancer\1.0'
USER_KEY_MAP = f'{platforms.HOME}/My Documents/My Games/Freelancer/UserKeyMap.ini'
DEFAULT_KEY_MAP = 'DATA/INTERFACE/keymap.ini'
CHAT_MESSAGE_MAX_LENGTH = 140


def get_user_keymap() -> Dict[str, str]:
    """Get the user's configured keymap."""
    try:
        return parse_keymap(USER_KEY_MAP)
    except FileNotFoundError:
        return parse_keymap(construct_path(DEFAULT_KEY_MAP))


def parse_keymap(keymap_file: str) -> Dict[str, str]:
    """Parse a Freelancer keymap file, like UserKeyMap.ini or keymap.ini, and convert keys to a format understood by
    the `keyboard` module."""
    key_map = ini.sections(keymap_file, fold_values=False)['keycmd']

    result = {}  # maps a command nicknames to its primary key binding

    for command in key_map:
        if 'key' not in command:
            continue
        nickname, key_combo = command['nickname'][0], command['key'][0]  # todo: only gets first to simply things

        # each "key" in the INI consists of exactly one VK code, and up to one modifier represented as a name
        if isinstance(key_combo, tuple):
            key, modifier = key_combo
        else:
            key, modifier = key_combo, ''

        if isinstance(key, int):  # keys are mostly in the form of virtual key codes
            try:
                name = virtual_key_to_name(key)
            except ValueError:
                warnings.warn(f'Key {nickname!r} in {keymap_file!r} maps to unknown virtual key: {key}')
                continue
        else:  # otherwise they are simply the key name in quotes
            name = key.strip('"')

        # finally, form into a string keyboard can understand
        formatted = '+'.join((name, modifier)) if modifier else name
        result[nickname] = formatted
    return result


if platforms.WIN32:
    from .win32 import get_active_account_name, virtual_key_to_name
elif platforms.LINUX:
    from .linux import get_active_account_name, virtual_key_to_name
