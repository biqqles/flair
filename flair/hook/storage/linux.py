"""
 Copyright (C) 2020 0cc4m.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import os.path

import virtualkeys

from ... import platforms
from .. import storage
from . import REGISTRY_DIR


USER_REGISTRY_FILE_PATH: str


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
            if line.startswith('"MPAccountName"='):
                return line.split('=')[1].replace('"', '')


def virtual_key_to_name(vk: int) -> str:
    """Get the name of a key from its VK (virtual key) code."""
    try:
        return virtualkeys.code_to_name[vk].partition('_')[2].lower()
    except KeyError:
        raise ValueError(f'Invalid virtual key: {vk}')


def set_wine_prefix_path(path: str):
    """Update the path to the registry and user key map."""
    users_path = os.path.join(path, 'drive_c/users/')
    users = set(os.listdir(users_path)) - {'Public'}
    user = next(iter(users))  # choose an arbitrary non-Public user

    global USER_REGISTRY_FILE_PATH
    storage.USER_KEY_MAP = storage.USER_KEY_MAP.replace(platforms.HOME, os.path.join(users_path, user), 1)
    USER_REGISTRY_FILE_PATH = os.path.join(path, 'user.reg')
    assert os.path.isfile(USER_REGISTRY_FILE_PATH)
