"""
 Copyright (C) 2020 0cc4m.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from typing import Tuple, Union, Optional

from Xlib.display import Display
from Xlib.error import BadWindow
from Xlib.X import RaiseLowest
from Xlib.xobject.drawable import Window

from . import WINDOW_TITLE


def find_window(name: str, window: Window) -> Optional[Window]:
    """Recursively locate a window with name `name` in the tree, starting at `window`."""
    if window.get_wm_name() == name:
        return window
    children = window.query_tree().children
    for child in children:
        val = find_window(name, child)
        if val:
            return val


def get_hwnd() -> Union[Window, int]:
    """Returns a non-zero window handle to Freelancer if a window exists, otherwise, returns zero."""
    try:
        return find_window(WINDOW_TITLE, Display().screen().root)
    except BadWindow:
        return 0


def is_foreground() -> bool:
    """Reports whether Freelancer is in the foreground and accepting input."""
    try:
        return Display().get_input_focus().focus.get_wm_name() == WINDOW_TITLE
    except (TypeError, AttributeError):
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
    """Remove the borders and titlebar from the game running in windowed mode."""
    raise NotImplementedError
