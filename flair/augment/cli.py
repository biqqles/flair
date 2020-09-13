import datetime

import flint
from ..inspect.state import FreelancerState

from . import Augmentation
from ..inspect.events import message_sent, character_changed
from ..hook import input
from .. import __version__


class CLI(Augmentation):
    """Adds a basic command-line interface."""
    INVOCATION = '..'

    class Command:
        """A command available in the in-game shell"""
        state: FreelancerState

        def __init__(self, state):
            self.state = state

        def __call__(self, *args, **kwargs):
            pass

    class Date(Command):
        """Print the local date and time"""

        def __call__(self):
            time = datetime.datetime.now()
            input.queue_display_text(time.strftime("%c"))  # formatted to locale

    class Sector(Command):
        """Print the current sector and system"""
        def __call__(self):
            if not self.state.system:
                input.queue_display_text(f'Err: unknown location')
            else:
                systems = {s.name(): s for s in flint.get_systems()}
                system_scale = systems[self.state.system].navmapscale
                sector = flint.maps.pos_to_sector(self.state.pos, system_scale)
                input.queue_display_text(f'You are in sector {sector}, {self.state.system}')

    class Eval(Command):
        """Evaluate the given expression with Python"""
        def __call__(self, *expression):
            if expression:
                try:
                    input.queue_display_text(f"=> {eval(' '.join(expression))}")
                except Exception as e:
                    input.queue_display_text(f"Err: {e}")

    class Quit(Command):
        """Quit the game"""
        def __call__(self):
            input.inject_keys('alt+f4')
            input.inject_keys('enter', after_delay=0.05)

    class Help(Command):
        """Show this help message"""
        def __call__(self):
            input.queue_display_text(f"flair version {__version__}")
            for c in self.__class__.__bases__[0].__subclasses__():
                input.queue_display_text(f'{CLI.INVOCATION}{c.__name__}: {c.__doc__}'.lower())

    def load(self):
        character_changed.connect(self.show_welcome_message)
        message_sent.connect(self.parse_message)

    def unload(self):
        character_changed.disconnect(self.show_welcome_message)
        message_sent.disconnect(self.parse_message)

    @staticmethod
    def show_welcome_message(name: str):
        """Greet the player on login."""
        input.queue_display_text(f"Welcome to Sirius, pilot. You're using flair {__version__}."
                                 " Type ..help to list a few commands.")

    def parse_message(self, message: str):
        """Parse and interpret a message."""
        preamble, invocation, command = message.strip().partition(self.INVOCATION)
        if invocation and not preamble:
            command_name, *args = [t for t in command.split()]
            commands = {c.__name__.lower(): c for c in self.Command.__subclasses__()}
            if command_name in commands:
                commands[command_name](self._state)(*args)
            else:
                input.queue_display_text('Err: command not found')
