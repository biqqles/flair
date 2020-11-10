"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from typing import Tuple

import win32con
import win32gui

from . import WINDOW_TITLE


def get_hwnd() -> int:
    """Returns a non-zero window handle to Freelancer if a window exists, otherwise, returns zero."""
    return win32gui.FindWindow(WINDOW_TITLE, WINDOW_TITLE)


def is_foreground() -> bool:
    """Reports whether Freelancer is in the foreground and accepting input."""
    return win32gui.GetForegroundWindow() == get_hwnd()


def make_foreground():
    """Bring Freelancer's window into the foreground and make it active."""
    hwnd = get_hwnd()
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)


def get_screen_coordinates() -> Tuple[int, int, int, int]:
    """Return the screen coordinates for the contents ("client"; excludes window decorations) of a Freelancer window."""
    hwnd = get_hwnd()
    left_x, top_y, right_x, bottom_y = win32gui.GetClientRect(hwnd)
    left_x, top_y = win32gui.ClientToScreen(hwnd, (left_x, top_y))  # convert "client" coordinates to screen coordinates
    right_x, bottom_y = win32gui.ClientToScreen(hwnd, (right_x, bottom_y))
    return left_x, top_y, right_x, bottom_y


def make_borderless():
    """Remove the borders and titlebar from the game running in windowed mode.
    Todo: Windowed mode seems to cut off the bottom of the game. This is something that will need worked around."""
    hwnd = get_hwnd()
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~win32con.WS_CAPTION  # remove border and titlebar
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

    titlebar_height = win32gui.GetWindowRect(hwnd)[3] - win32gui.GetClientRect(hwnd)[3]
    # move the window up to compensate for the lack of a titlebar
    # the two flags result in the second, fifth and six arguments being ignored so we don't have to worry about them
    win32gui.SetWindowPos(hwnd, 0, 0, -titlebar_height, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
