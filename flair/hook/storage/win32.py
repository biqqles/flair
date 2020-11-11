"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import ctypes
import winreg

import win32api

from . import REGISTRY_DIR


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
