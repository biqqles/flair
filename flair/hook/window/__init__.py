import sys

WINDOW_TITLE = 'Freelancer'


if sys.platform.startswith('win32'):
    from .win32 import get_hwnd, is_foreground, make_foreground, get_screen_coordinates, make_borderless
elif sys.platform.startswith('linux'):
    from .linux import get_hwnd, is_foreground, make_foreground, get_screen_coordinates, make_borderless


def is_present() -> bool:
    """Reports whether Freelancer is running."""
    return bool(get_hwnd())
