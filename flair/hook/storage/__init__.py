"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import os.path

from ... import platforms

REGISTRY_DIR = r'Software\Microsoft\Microsoft Games\Freelancer\1.0'
USER_KEY_MAP = os.path.expanduser(r'~\Documents\My Games\Freelancer\UserKeyMap.ini')
CHAT_MESSAGE_MAX_LENGTH = 140

if platforms.WIN32:
    from .win32 import get_active_account_name, virtual_key_to_name, get_user_keymap
elif platforms.LINUX:
    pass
