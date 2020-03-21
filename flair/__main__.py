"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import argparse
import os

from . import events, augment
from . import FreelancerState


if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser(prog='flair', description='flair, a novel client-side hook for Freelancer')
    parser.add_argument('freelancer_dir', help='Path to a working Freelancer install directory')
    arguments = parser.parse_args()

    # enable ANSI colour codes on Windows
    os.system('color')

    def print_event(*args):
        """Print an event to terminal with emphasis (using ANSI colour codes). How this displays exactly varies between
        terminals."""
        print('\033[1m' + ' '.join(map(str, args)) + '\033[0m')

    events.message_sent.connect(lambda message: print_event('Message sent:', message))
    events.freelancer_started.connect(lambda: print_event('Freelancer started'))
    events.freelancer_stopped.connect(lambda: print_event('Freelancer stopped'))
    events.system_changed.connect(lambda system: print_event('System entered:', system))
    events.docked.connect(lambda base: print_event('Docked at:', base))
    events.undocked.connect(lambda: print_event('Undocked from base'))
    events.credits_changed.connect(lambda balance: print_event('Credit balance changed:', balance))
    events.character_changed.connect(lambda name: print_event('Character loaded:', name))
    events.account_changed.connect(lambda name: print_event('Account loaded:', name))
    events.chat_box_opened.connect(lambda: print_event('Chat box opened'))
    events.chat_box_closed.connect(
        lambda message_sent: print_event('Chat box closed, message', f'{"" if message_sent else "un"}sent'))
    events.switched_to_foreground.connect(lambda: print_event('Freelancer switched to foreground'))
    events.switched_to_background.connect(lambda: print_event('Freelancer switched to background'))

    game_state = FreelancerState(arguments.freelancer_dir)
    game_state.begin_polling()
    augmentations = augment.Augmentation.load_all(game_state)
