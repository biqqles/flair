"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from ... import platforms

WINDOW_TITLE = 'Freelancer'


def is_present() -> bool:
    """Reports whether Freelancer is running."""
    return bool(get_hwnd())


if platforms.WIN32:
    from .win32 import get_hwnd, is_foreground, make_foreground, get_screen_coordinates, make_borderless
elif platforms.LINUX:
    from .linux import get_hwnd, is_foreground, make_foreground, get_screen_coordinates, make_borderless
