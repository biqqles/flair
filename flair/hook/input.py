"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from types import FunctionType

from .. import IS_ADMIN

if not IS_ADMIN:
    raise ImportError('flair must be run as administrator to be able to hook keyboard input in Freelancer')

import time
from typing import List, Tuple

import keyboard as keyboard

from . import process, window, storage
from ..inspect.events import message_sent, chat_box_closed, chat_box_opened  # emits
from ..inspect.events import switched_to_background, switched_to_foreground  # utilises

INDENT = ' ' * 4
ECHO_PREAMBLE = '|=|  '
KEY_SEND_MESSAGE = 'enter'  # unlike the hotkey to open the chat box, these keys are hardcoded
KEY_CLOSE_CHAT_BOX = 'esc'
KEY_CHANGE_CHAT_CHANNEL = 'up'

chat_box_events: List[keyboard.KeyboardEvent] = []
message_queue: List[str] = []  # messages to be shown to player
hotkeys: List[Tuple[str, FunctionType]] = []


def bind_hotkey(combination, function):
    """Adds a hotkey which is only active when Freelancer is in the foreground."""
    assert callable(function)
    hotkeys.append((combination, function))


def unbind_hotkey(combination, function):
    """Removes a hotkey that has been bound in the Freelancer window."""
    hotkeys.remove((combination, function))


def queue_display_text(text: str):
    """Queue text to be displayed to the user. If Freelancer is in the foreground and the chat box is closed,
    this will be shown immediately. Otherwise, the text will be shown as soon as both these conditions are true."""
    time.sleep(.1)  # wait for chat box state to propagate
    if window.is_foreground() and not process.get_chat_box_state(process.get_process()):  # show immediately
        send_message(text)
    else:
        message_queue.append(text)


def send_message(message: str, private=True):
    """Inserts `message` into the chat box and sends it. If `private` is true, send to the Console."""
    assert window.is_foreground(), not process.get_chat_box_state(process.get_process())
    text = str(message).encode('ascii', errors='ignore').decode()  # strip out all non-ascii characters
    inject_keys(get_chat_box_open_hotkey())  # open chat box
    if private:
        inject_keys(KEY_CHANGE_CHAT_CHANNEL, after_delay=.001)  # switch to Console (private to player)
        text = ECHO_PREAMBLE + text
    keyboard.write(text)
    keyboard.send(KEY_SEND_MESSAGE)


def inject_keys(key: str, after_delay=0.0):
    """Inject a key combination into the Freelancer window."""
    assert window.is_foreground()
    time.sleep(after_delay)
    keyboard.send(key)


def inject_text(text: str):
    """Inject text into the chat box."""
    assert process.get_chat_box_state(process.get_process())
    keyboard.write(text)


def initialise_hotkey_hooks():
    """Initialise hotkey hooks for Freelancer. Should be run when, and only when, the Freelancer window is brought into
    the foreground."""
    assert IS_ADMIN, window.is_present()
    # the user_chat hotkey always opens the chat box, no matter which other dialogues are up
    box_initially_open = process.get_chat_box_state(process.get_process())
    if box_initially_open:
        on_chat_box_opened()
    else:
        on_chat_box_closed()

    # hook registered hotkeys
    for k, f in hotkeys:
        keyboard.add_hotkey(k, f)


def terminate_hotkey_hooks():
    """Release hotkey hooks for Freelancer. Should be run when, and only when, the Freelancer window is put into the
    background."""
    try:
        keyboard.remove_all_hotkeys()
    except AttributeError:
        pass  # a bug in keyboard (todo: submit PR)
    finally:
        keyboard.unhook_all()


def on_chat_box_opened():
    """Handle the user opening the chat box. Emits the `chat_box_opened` signal."""
    if window.is_foreground():
        handle = process.get_process()
        if _wait_until(lambda: process.get_chat_box_state(handle)):
            terminate_hotkey_hooks()
            # begin capturing keystrokes
            keyboard.hook(collect_chat_box_events)
            # add hooks for close
            keyboard.add_hotkey(KEY_SEND_MESSAGE, on_chat_box_closed, args=[False])
            keyboard.add_hotkey(KEY_CLOSE_CHAT_BOX, on_chat_box_closed, args=[True])
            # emit signal
            chat_box_opened.emit()
        else:
            initialise_hotkey_hooks()


def on_chat_box_closed(cancelled=False):
    """Handle the user closing the chat box. Emits the `chat_box_closed` signal."""
    if window.is_foreground():
        handle = process.get_process()
        if _wait_until(lambda: not process.get_chat_box_state(handle)):
            # print queued messages
            if process.get_character_loaded(process.get_process()):
                while message_queue:
                    send_message(message_queue.pop(0))
            # emit signals
            contents = get_chat_box_contents()
            sent = not cancelled and contents
            chat_box_closed.emit(message_sent=sent)
            if sent:
                message_sent.emit(message=contents)  # todo: may want to compare to process.get_last_message
            terminate_hotkey_hooks()
            # add hook for open
            keyboard.add_hotkey(get_chat_box_open_hotkey(), on_chat_box_opened)
            # clear events
            chat_box_events.clear()
        else:
            initialise_hotkey_hooks()


def collect_chat_box_events(event):
    """Handle a keyboard event while the chat box is open.
    # Todo: handle arrow keys, copy and paste"""
    if window.is_foreground():
        chat_box_events.append(event)


def get_chat_box_contents():
    """Return (our best guess at) the current contents of the chat box. If it is closed, returns a blank string."""
    return ''.join(keyboard.get_typed_strings(chat_box_events, allow_backspace=True))


def get_chat_box_open_hotkey():
    """Return the hotkey configured to open the chat box."""
    return storage.get_user_keymap()['user_chat']


def _wait_until(condition, timeout=0.1):
    """Block until condition returns True, or the timeout (in seconds) is reached. Return True if condition became
    true before the timeout, otherwise False."""
    start = time.time()
    while not condition() and (time.time() - start) < timeout:
        continue
    return condition()


switched_to_foreground.connect(initialise_hotkey_hooks)
switched_to_background.connect(terminate_hotkey_hooks)
