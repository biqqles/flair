"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import ctypes
import errno

from pywintypes import HANDLE
import win32api
import win32process
import win32con

from ..window import get_hwnd
from . import buffer_as_utf16


PROCESS_VM_READ = 0x10  # <https://msdn.microsoft.com/en-us/library/windows/desktop/ms684880(v=vs.85).aspx>


def get_process() -> HANDLE:
    """Return a handle to Freelancer's process."""
    hwnd = get_hwnd()
    pid = win32process.GetWindowThreadProcessId(hwnd)[1]
    try:
        process = win32api.OpenProcess(win32con.PROCESS_VM_READ, 0, pid)
    except win32api.error as e:
        if e.winerror == 5:
            raise PermissionError(errno.EPERM, f'{e.funcname}: {e.strerror} (WinError {e.winerror})') from e
        raise
    return process


def read_memory(process: HANDLE, address: int, datatype: type, buffer_size=128):
    """Reads Freelancer's process memory.

    Just as with string resources, strings are stored as UTF-16 meaning that the end of a string is marked by two
    consecutive null bytes. However, other bytes will be present in the buffer after these two nulls since it is of
    arbitrary size, and these confuse Python's builtin .decode and result in UnicodeDecodeError. So we can't use it.
    """
    buffer = ctypes.create_string_buffer(buffer_size)
    value = datatype()
    handle = process if isinstance(process, int) else process.handle

    if ctypes.windll.kernel32.ReadProcessMemory(handle, address, buffer, len(buffer), 0):
        if datatype is str:
            value = buffer_as_utf16(buffer)
        else:
            ctypes.memmove(ctypes.byref(value), buffer, ctypes.sizeof(value))
            value = value.value  # C type -> Python type, effectively
    return value
