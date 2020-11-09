from ctypes import *
import os
from subprocess import check_output, CalledProcessError


class iovec(Structure):
    _fields_ = [("iov_base", c_void_p), ("iov_len", c_size_t)]


def get_process():
    """Return a handle to Freelancer's process."""
    try:
        return int(check_output(['pidof', 'Freelancer.exe']))
    except CalledProcessError:
        return 0


def _c_char_array_to_utf16_array(buf):
    return [buf[i] + buf[i + 1] for i in range(0, len(buf), 2)]


def _c_char_array_to_str(buf):
    utf16_array = _c_char_array_to_utf16_array(buf)
    result = []
    for utf_char in utf16_array:
        if utf_char == b'\x00\x00':
            break

        try:
            result.append(utf_char.decode('UTF-16'))
        except UnicodeDecodeError:
            break
    return ''.join(result)


def read_memory(process, address: int, datatype: type, buffer_size=128):
    """Reads Freelancer's process memory.

    Just as with string resources, strings are stored as UTF-16 meaning that the end of a string is marked by two
    consecutive null bytes. However, other bytes will be present in the buffer after these two nulls since it is of
    arbitrary size, and these confuse Python's builtin .decode and result in UnicodeDecodeError. So we can't use it.
    """
    ensure_root()
    if datatype is str:
        buffer_size_2 = buffer_size * 2
        local = (iovec * buffer_size)()
        remote = (iovec * 1)()
        buf1 = (c_char * buffer_size_2)()

        for i in range(0, buffer_size):
            local[i].iov_base = cast(byref(buf1, 2*i), c_void_p)
            local[i].iov_len = 2
        remote[0].iov_base = c_void_p(address)
        remote[0].iov_len = 2 * buffer_size

        libc = CDLL("libc.so.6")
        vm = libc.process_vm_readv

        vm.argtypes = [c_int, POINTER(iovec), c_ulong,
                       POINTER(iovec), c_ulong, c_ulong]

        nread = vm(process, local, buffer_size, remote, 1, 0)

        if nread != -1:
            return _c_char_array_to_str(buf1)
        else:
            return ""
    else:
        local = (iovec*1)()
        remote = (iovec*1)()
        buf1 = (datatype*1)()

        local[0].iov_base = cast(byref(buf1), c_void_p)
        local[0].iov_len = sizeof(datatype)
        remote[0].iov_base = c_void_p(address)
        remote[0].iov_len = sizeof(datatype)

        libc = CDLL("libc.so.6")
        vm = libc.process_vm_readv

        vm.argtypes = [c_int, POINTER(iovec), c_ulong,
                       POINTER(iovec), c_ulong, c_ulong]

        nread = vm(process, local, 1, remote, 1, 0)

        if nread != -1:
            return buf1[0]
        else:
            return


def ensure_root():
    if os.geteuid() != 0:
        raise ImportError('You must be root to use this library on linux.')
