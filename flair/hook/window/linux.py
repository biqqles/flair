"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from typing import Tuple

from Xlib.display import Display
from Xlib.error import BadWindow
from Xlib.X import RaiseLowest

from . import WINDOW_TITLE


def get_hwnd() -> int:
    """Returns a non-zero window handle to Freelancer if a window exists, otherwise, returns zero."""
    def find_window(name, window):
        if window.get_wm_name() == name:
            return window
        children = window.query_tree().children
        for child in children:
            val = find_window(name, child)
            if val:
                return val

    display = Display()

    try:
        fl_window = find_window(WINDOW_TITLE, display.screen().root)
    except BadWindow:
        return 0

    if fl_window:
        return fl_window
    else:
        return 0


def is_foreground() -> bool:
    """Reports whether Freelancer is in the foreground and accepting input."""
    try:
        return Display().get_input_focus().focus.get_wm_name() == WINDOW_TITLE
    except TypeError:
        return False


def make_foreground():
    """Bring Freelancer's window into the foreground and make it active."""
    hwnd = get_hwnd()
    hwnd.circulate(RaiseLowest)


def get_screen_coordinates() -> Tuple[int, int, int, int]:
    """Return the screen coordinates for the contents ("client"; excludes window decorations) of a Freelancer window."""
    hwnd = get_hwnd()
    geo = hwnd.query_tree().parent.get_geometry()._data
    left_x = geo['x']
    top_y = geo['y']
    right_x = left_x + geo['width']
    bottom_y = top_y + geo['height']
    return left_x, top_y, right_x, bottom_y


def make_borderless():
    """Remove the borders and titlebar from the game running in windowed mode.
    Todo: Windowed mode seems to cut off the bottom of the game. This is something that will need worked around."""
    raise NotImplementedError
