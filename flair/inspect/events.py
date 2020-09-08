"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""


class Signal(set):
    """A simple event object inspired by Qt's signals and slots mechanism."""

    def __init__(self, **schema):
        """`schema` is a description of the data this signal is intended to send to connected functions when emitted."""
        super().__init__()
        self.schema = schema

    def connect(self, function):
        """Connect this signal to a function. This means that it will be called when the signal is emitted."""
        self.add(function)

    def disconnect(self, function):
        """Disconnect this signal from a function."""
        if function in self:
            self.remove(function)

    def disconnect_all(self):
        """Disconnect all functions from this signal."""
        self.clear()

    def emit(self, **payload):
        """Emit this signal, causing all connected functions to be executed with `payload` sent as keyword arguments."""
        if not set(payload) == set(self.schema):  # compare keys
            raise ValueError('Payload does not conform to the schema specified for this signal')
        for function in self:
            function(**payload)


# /Name/                                     # /Emitted when/                           # /Parameter(s)/
character_changed = Signal(name=str)         # New character loaded                     # New character name
account_changed = Signal(account=str)        # Active (registry) account changed        # New account code
system_changed = Signal(system=str)          # New system entered                       # New system display name
docked = Signal(base=str)                    # Docked base (respawn point) changed      # New base display name
undocked = Signal()                          # Undocked from base                       # N/A
credits_changed = Signal(balance=int)        # Credit balance changed                   # New credit balance
message_sent = Signal(message=str)           # New message sent by player               # Message text
chat_box_opened = Signal()                   # Chat box opened                          # N/A
chat_box_closed = Signal(message_sent=bool)  # Chat box closed                          # Whether message sent
freelancer_started = Signal()                # Freelancer process launched              # N/A
freelancer_stopped = Signal()                # Freelancer process closed                # N/A
switched_to_foreground = Signal()            # Freelancer switched to foreground        # N/A
switched_to_background = Signal()            # Freelancer switched to background        # N/A
