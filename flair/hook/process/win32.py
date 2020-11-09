from ctypes import *
import errno
from pywintypes import HANDLE
import win32api
import win32process
import win32con

from ..window import get_hwnd


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
    buffer = create_string_buffer(buffer_size)
    value = datatype()
    handle = process if isinstance(process, int) else process.handle

    if windll.kernel32.ReadProcessMemory(handle, address, buffer, len(buffer), 0):
        if datatype is str:
            value = buffer.raw.decode('utf-16').partition('\0')[0]
        else:
            memmove(byref(value), buffer, sizeof(value))
            value = value.value  # C type -> Python type, effectively
    return value
