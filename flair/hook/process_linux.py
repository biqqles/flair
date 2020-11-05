"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from typing import Tuple
from ctypes import *

from subprocess import check_output, CalledProcessError
import os


class iovec(Structure):
    _fields_ = [("iov_base", c_void_p), ("iov_len", c_size_t)]


# useful addresses to read from. These are all static, obviously. In the future I may look for static pointers to
# dynamic addresses. Offsets correct for v1.1 executable.
READ_ADDRESSES = {
    'last_message':   (0x66D4F2, str),
    'mouseover':      (0x66DC60, str),
    'rollover':       (0x66FC60, str),  # seems to show rollover help, solar rollovers and information dialogue text
    'name':           (0x6732F0, str),
    'credits':        (0x673364, c_uint),
    'pos_x':          (0x6732E4, c_float),
    'pos_y':          (0x6732E8, c_float),
    'pos_z':          (0x6732EC, c_float),
    'enter_dialogue': (0x67C3AC, c_uint32),  # seems to be nonzero for dialogues that hook enter
    'focus_dialogue': (0x667D54, c_uint32),  # true for dialogues which darken the screen - pause menu and exit game
    'logged_in':      (0x67E9D4, c_uint32),  # whether player is logged in (whether in SP or to a MP server)
    'singleplayer':   (0x67334C, c_uint32),  # whether player is loaded into SP
    'in_space':       (0x673560, c_uint32),  # whether the player is in space (not docked) (possibly also 0x673530)
}


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


def get_value(process, key, size=None):
    """Read a value from memory. `key` refers to the key of an address in `READ_ADDRESSES`"""
    address, datatype = READ_ADDRESSES[key]
    return read_memory(process, address, datatype, buffer_size=size or (sizeof(datatype) * 8))


def get_string(process, key, length):
    """Read a UTF-16 string from memory."""
    return get_value(process, key, (length * 2) + 2)


def get_name(process) -> str:
    """Read the name of the active character from memory."""
    return get_string(process, 'name', 23)


def get_credits(process) -> int:
    """Read the credit balance of the active character from memory."""
    return get_value(process, 'credits')


def get_position(process) -> Tuple[float, float, float]:
    """Read the position of the active character from memory."""
    return get_value(process, 'pos_x'), get_value(process, 'pos_y'), get_value(process, 'pos_z')


def get_mouseover(process) -> str:
    """This is a really interesting address. It seems to store random, unconnected pieces of text that have been
    recently displayed or interacted with in the game. These range from console outputs to the names of bases
    and planets immediately upon jumping in or docking, to the prices of commodities in the trader screen, to
    mission "popups" messages, to the name of some solars and NPCs that are moused over while in space.
    With some imagination this can probably be put to some use..."""
    return get_string(process, 'mouseover', 128)


def get_rollover(process) -> str:
    """Similar to mouseover, but usually contains tooltip text."""
    return get_string(process, 'rollover', 128)


def get_last_message(process) -> str:
    """Read the last message sent by the player from memory"""
    return get_string(process, 'last_message', 127)


def get_chat_box_state(process) -> bool:
    """Read the state of the chat box from memory."""
    dialogue_hooking_enter = get_value(process, 'enter_dialogue')
    dialogue_focused = get_value(process, 'focus_dialogue')
    return bool(dialogue_hooking_enter and not dialogue_focused)


def get_character_loaded(process) -> bool:
    """Read whether a character is loaded (whether in SP or MP)."""
    return bool(get_value(process, 'logged_in'))


def get_docked(process) -> bool:
    """Read whether the active character is docked."""
    return not bool(get_value(process, 'in_space'))


def ensure_root():
    if os.geteuid() != 0:
        raise ImportError('You must be root to use this library on linux.')
