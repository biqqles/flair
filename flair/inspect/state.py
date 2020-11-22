"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import threading
from typing import Optional

import flint as fl
from flint.maps import PosVector

from ..inspect import events
from ..hook import window, process, storage


class state_variable:
    def __init__(self, initially, passive=False):
        """Handle arguments to decorator.
        `initially`: the initial value of this variable
        `passive`: if true, signifies that the getter does not compute the value of the variable - i.e. it is set
        elsewhere."""
        self.default = initially
        self.last = initially
        self.passive = passive

    def __call__(self, getter):
        """Handle first function passed to decorator."""
        self.fget = getter
        self.__doc__ = getter.__doc__
        self.fchanged = lambda *args: None
        return self

    def __get__(self, instance, owner):
        """Return the current value of the state variable. If the game is not running, this is the default value."""
        if not window.is_present():
            return self.default
        else:
            if self.passive:
                return self.last
            return self.fget(instance)

    def __set__(self, instance, value):
        """Handle state variable being updated."""
        if value != self.last:
            self.fchanged(instance, value, self.last)
            self.last = value

    def changed(self, fchanged):
        """Handle second function passed to decorator."""
        if not hasattr(self, 'fget'):
            raise TypeError('A "get" function must be set before this decorator can be applied.')
        self.fchanged = fchanged
        return self


class FreelancerState:
    """An object which holds the state of the game and emits most of flair's events when it detects that a variable has
    changed."""
    def __init__(self, freelancer_root):
        fl.paths.set_install_path(freelancer_root)
        self._systems = {s.name() for s in fl.get_systems() if s.name()}
        self._bases = {b.name() for b in fl.get_bases() if b.name()}
        self._timer = None
        self._process = 0
        self.begin_polling()

    def __str__(self):
        return (f'State(running={self.running}, '
                f'foreground={self.foreground}, '
                f'chat_box={self.chat_box}, '
                f'char_loaded={self.character_loaded}, '
                f'character_name={self.name!r}, '
                f'system={self.system!r}, '
                f'base={self.base!r}, '
                f'docked={self.docked!r}, '
                f'credits={self.credits}, '
                f'pos={self.pos!r})')

    def refresh(self):
        """Cause state variables to refresh themselves."""
        self.running = self.running
        self.foreground = self.foreground

        if self.running:  # remember to add new properties here or they will not be polled
            self.character_loaded = self.character_loaded
            self.name = self.name
            self.credits = self.credits
            self.pos = self.pos
            self.docked = self.docked
            self.mouseover = self.mouseover
            self.chat_box = self.chat_box

    def begin_polling(self, period=1.0, print_state=False):
        """Begin polling the game's state and emitting events. Called upon instantiation by default. If `print_state`
        is true, the instance's repr will be printed on each refresh."""
        def poll():
            self.refresh()
            if print_state:
                print(self)
            self._timer = threading.Timer(period, poll)
            self._timer.start()

        self.end_polling()
        poll()

    def end_polling(self):
        """Stop polling the game's state and emitting events."""
        if self._timer:
            self._timer.cancel()

    @state_variable(initially=False)
    def running(self) -> bool:
        """Whether an instance of the game is running."""
        return window.is_present()

    @running.changed
    def running(self, new, last):
        if new:  # Freelancer has been started
            self._process = process.get_process()
            events.freelancer_started.emit()
        else:  # Freelancer has been stopped
            if self._process and type(self._process) is not int:
                self._process.close()
            events.freelancer_stopped.emit()

    @state_variable(initially=False)
    def foreground(self) -> bool:
        """Whether an instance of the game is in the foreground and accepting input."""
        return window.is_foreground() if self.running else False

    @foreground.changed
    def foreground(self, new, last):
        if new:
            events.switched_to_foreground.emit()
        else:
            events.switched_to_background.emit()

    @state_variable(initially=False)
    def chat_box(self) -> bool:
        """Whether the chat box is open."""
        return process.get_chat_box_state(self._process)

    @chat_box.changed
    def chat_box(self, new, last):
        return  # passive - handled by input.py

    @state_variable(initially='')
    def account(self) -> str:
        """The "name" (hash) of the currently active account, taken from the registry."""
        return storage.get_active_account_name()

    @account.changed
    def account(self, new, last):
        events.account_changed.emit(account=new)

    @state_variable(initially='')
    def mouseover(self) -> str:
        """See documentation in hook/process."""
        return process.get_mouseover(self._process)

    @mouseover.changed
    def mouseover(self, new, last):
        if new in self._systems:
            # player has entered a new system
            self.system = new

    @state_variable(initially=False)
    def character_loaded(self) -> bool:
        """Whether a character is currently loaded (i.e. the player is logged in), either in SP or MP."""
        return process.get_character_loaded(self._process)

    @character_loaded.changed
    def character_loaded(self, new, last):
        # Freelancer loads the current account from registry on server connection, so this is a good time to get it
        if new:
            self.account = self.account
        else:
            self.system = None
            self.base = None

    @state_variable(initially=None)
    def name(self) -> Optional[str]:
        """The name of the currently active character if there is one, otherwise None."""
        return process.get_name(self._process) if self.character_loaded else None

    @name.changed
    def name(self, new, last):
        events.character_changed.emit(name=new)

    @state_variable(initially=None)
    def credits(self) -> Optional[int]:
        """The number of credits the active character has if there is one, otherwise None."""
        return process.get_credits(self._process) if self.character_loaded else None

    @credits.changed
    def credits(self, new, last):
        events.credits_changed.emit(balance=new)

    @state_variable(initially=None, passive=True)
    def system(self) -> Optional[str]:
        """The display name (e.g. "New London") of the system the active character is in if there is one, otherwise
        None."""
        return  # passive - set in mouseover

    @system.changed
    def system(self, new, last):
        events.system_changed.emit(system=new)

    @state_variable(initially=None, passive=True)
    def base(self) -> Optional[str]:
        """The display name (e.g. "The Ring") of the base the active character last docked at if there is one,
        otherwise None."""
        return  # passive - set in docked

    @state_variable(initially=None)
    def docked(self) -> Optional[bool]:
        """Whether the active character is presently docked at a base if there is one, otherwise None."""
        return process.get_docked(self._process) if self.character_loaded else None

    @docked.changed
    def docked(self, new, last):
        if new and self.mouseover in self._bases:  # todo: try wait_until(self.mouseover)
            self.base = self.mouseover
            events.docked.emit(base=self.base)
        elif not new:
            events.undocked.emit()

    @state_variable(initially=None)
    def pos(self) -> Optional[PosVector]:
        """The position vector of the active character if there is one, otherwise None."""
        return PosVector(*process.get_position(self._process)) if self.character_loaded else None
