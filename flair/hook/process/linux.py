"""
 Copyright (C) 2020 biqqles.
 Copyright (C) 2020 0cc4m.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import ctypes
from subprocess import check_output, CalledProcessError

from . import buffer_as_utf16


libc = ctypes.CDLL('libc.so.6')
process_vm_read = libc.process_vm_readv  # <https://linux.die.net/man/2/process_vm_readv>


class iovec(ctypes.Structure):
    _fields_ = [('iov_base', ctypes.c_void_p),
                ('iov_len', ctypes.c_size_t)]


process_vm_read.argtypes = [ctypes.c_int, ctypes.POINTER(iovec), ctypes.c_ulong,
                            ctypes.POINTER(iovec), ctypes.c_ulong, ctypes.c_ulong]


def get_process() -> int:
    """Return a handle to Freelancer's process."""
    try:
        return int(check_output(['pidof', 'Freelancer.exe']))
    except CalledProcessError:
        return 0


def read_memory(process, address: int, datatype: type, buffer_size=128):
    """Reads Freelancer's process memory.

    Just as with string resources, strings are stored as UTF-16 meaning that the end of a string is marked by two
    consecutive null bytes. However, other bytes will be present in the buffer after these two nulls since it is of
    arbitrary size, and these confuse Python's builtin .decode and result in UnicodeDecodeError. So we can't use it.
    """
    local = (iovec * 1)()
    remote = (iovec * 1)()

    if datatype is str:
        buffer = ctypes.create_string_buffer(buffer_size)
    else:
        buffer = (datatype * 1)()
        buffer_size = ctypes.sizeof(datatype)

    local[0].iov_base = ctypes.cast(ctypes.byref(buffer), ctypes.c_void_p)
    local[0].iov_len = buffer_size
    remote[0].iov_base = ctypes.c_void_p(address)
    remote[0].iov_len = buffer_size

    if process_vm_read(process, local, len(local), remote, len(remote), 0):
        return buffer_as_utf16(buffer) if datatype is str else buffer[0]
    return datatype()
