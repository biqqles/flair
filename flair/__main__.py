"""
 Copyright (C) 2016, 2017, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import argparse
import os
import sys

from . import events, augment, hook, inspect
from . import FreelancerState
from . import set_install_path
from . import get_state

import rpyc
from rpyc.utils.server import OneShotServer


class FlairService(rpyc.Service):
    exposed_hook = hook
    exposed_augment = augment
    exposed_inspect = inspect
    exposed_events = events
    exposed_FreelancerState = FreelancerState

    def __init__(self, wine_prefix_dir):
        self.wine_prefix_dir = wine_prefix_dir

    def exposed_set_install_path(self, path):
        set_install_path(path, self.wine_prefix_dir)

    def exposed_get_state(self):
        return get_state()


if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser(prog='flair', description='flair, a novel client-side hook for Freelancer')
    parser.add_argument('freelancer_dir', help='Path to a working Freelancer install directory')
    if sys.platform.startswith('linux'):
        parser.add_argument('-r', '--rpyc', action='store_true')
        parser.add_argument('-p', '--port', default=18861, type=int)
        parser.add_argument('freelancer_wine_prefix_dir', help='Path to the wine prefix containing Freelancer')
    arguments = parser.parse_args()

    # enable ANSI colour codes on Windows
    if sys.platform.startswith('win32'):
        os.system('color')

    def print_event(*args):
        """Print an event to terminal with emphasis (using ANSI colour codes). How this displays exactly varies between
        terminals."""
        print('\033[1m' + ' '.join(map(str, args)) + '\033[0m')

    if arguments.rpyc:
        t = OneShotServer(
            FlairService(arguments.freelancer_wine_prefix_dir),
            port=arguments.port,
            protocol_config={
                'allow_public_attrs': True,
            },
        )
        t.start()
        os._exit(0)

    events.message_sent.connect(lambda message: print_event('Message sent:', message))
    events.freelancer_started.connect(lambda: print_event('Freelancer started'))
    events.freelancer_stopped.connect(lambda: print_event('Freelancer stopped'))
    events.system_changed.connect(lambda system: print_event('System entered:', system))
    events.docked.connect(lambda base: print_event('Docked at:', base))
    events.undocked.connect(lambda: print_event('Undocked from base'))
    events.credits_changed.connect(lambda balance: print_event('Credit balance changed:', balance))
    events.character_changed.connect(lambda name: print_event('Character loaded:', name))
    events.account_changed.connect(lambda account: print_event('Account loaded:', account))
    events.chat_box_opened.connect(lambda: print_event('Chat box opened'))
    events.chat_box_closed.connect(
        lambda message_sent: print_event('Chat box closed, message', f'{"" if message_sent else "un"}sent'))
    events.switched_to_foreground.connect(lambda: print_event('Freelancer switched to foreground'))
    events.switched_to_background.connect(lambda: print_event('Freelancer switched to background'))

    if sys.platform.startswith('linux'):
        fl_wine_prefix_dir = arguments.freelancer_wine_prefix_dir
    else:
        fl_wine_prefix_dir = None

    game_state = FreelancerState(arguments.freelancer_dir, fl_wine_prefix_dir)
    game_state.begin_polling(print_state=False)
    augmentations = augment.Augmentation.load_all(game_state)
