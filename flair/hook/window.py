"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from typing import Tuple

import sys

if sys.platform.startswith('win32'):
    import win32con
    import win32gui
elif sys.platform.startswith('linux'):
    from Xlib.display import Display
    from Xlib.error import BadWindow
    from Xlib.X import RaiseLowest


def get_hwnd() -> int:
    """Returns a non-zero window handle to Freelancer if a window exists, otherwise, returns zero."""
    if sys.platform.startswith('win32'):
        return win32gui.FindWindow(WINDOW_TITLE, WINDOW_TITLE)
    elif sys.platform.startswith('linux'):
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


def is_present() -> bool:
    """Reports whether Freelancer is running."""
    return bool(get_hwnd())


def is_foreground() -> bool:
    """Reports whether Freelancer is in the foreground and accepting input."""
    if sys.platform.startswith('win32'):
        return win32gui.GetForegroundWindow() == get_hwnd()
    elif sys.platform.startswith('linux'):
        try:
            return Display().get_input_focus().focus.get_wm_name() == WINDOW_TITLE
        except TypeError:
            return False


def make_foreground():
    """Bring Freelancer's window into the foreground and make it active."""
    hwnd = get_hwnd()
    if sys.platform.startswith('win32'):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
    elif sys.platform.startswith('linux'):
        hwnd.circulate(RaiseLowest)


def get_screen_coordinates() -> Tuple[int, int, int, int]:
    """Return the screen coordinates for the contents ("client"; excludes window decorations) of a Freelancer window."""
    hwnd = get_hwnd()
    if sys.platform.startswith('win32'):
        left_x, top_y, right_x, bottom_y = win32gui.GetClientRect(hwnd)
        left_x, top_y = win32gui.ClientToScreen(hwnd, (left_x, top_y))  # convert "client" coordinates to screen coordinates
        right_x, bottom_y = win32gui.ClientToScreen(hwnd, (right_x, bottom_y))
    elif sys.platform.startswith('linux'):
        geo = hwnd.query_tree().parent.get_geometry()._data
        left_x = geo['x']
        top_y = geo['y']
        right_x = left_x + geo['width']
        bottom_y = top_y + geo['height']
    return left_x, top_y, right_x, bottom_y


def make_borderless():
    """Remove the borders and titlebar from the game running in windowed mode.
    Todo: Windowed mode seems to cut off the bottom of the game. This is something that will need worked around."""
    if sys.platform.startswith('win32'):
        hwnd = get_hwnd()
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style &= ~win32con.WS_CAPTION  # remove border and titlebar
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

        titlebar_height = win32gui.GetWindowRect(hwnd)[3] - win32gui.GetClientRect(hwnd)[3]
        # move the window up to compensate for the lack of a titlebar
        # the two flags result in the second, fifth and six arguments being ignored so we don't have to worry about them
        win32gui.SetWindowPos(hwnd, 0, 0, -titlebar_height, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
    elif sys.platform.startswith('linux'):
        raise NotImplementedError


WINDOW_TITLE = 'Freelancer'
