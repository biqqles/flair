"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import sys

if sys.platform.startswith('win32'):
    from .win32 import get_active_account_name, virtual_key_to_name, get_user_keymap
elif sys.platform.startswith('linux'):
    from .linux import get_active_account_name, virtual_key_to_name, get_user_keymap, set_wine_prefix_path
