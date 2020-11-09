"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from typing import Tuple
from ctypes import *
import sys

if sys.platform.startswith('win32'):
    from .win32 import get_process, read_memory
elif sys.platform.startswith('linux'):
    from .linux import get_process, read_memory

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
