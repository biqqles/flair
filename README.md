# flair
**flair** (*FreeLancer Augmentation and Inspection at Runtime*) is a client-side hook for the 2003 space sim [*Freelancer*](https://en.wikipedia.org/wiki/Freelancer_%28video_game%29) which requires no changes to the game files and no code to be injected into the game's process.

flair achieves this through a combination of hooking user input, reading process memory and window interaction using the Win32 API, and an understanding of Freelancer's static data provided by [flint](https://github.com/biqqles/flint). Through these means flair allows the game's state to be inspected in real-time. It also allows the game client to be augmented, for example adding clipboard access to the game's chat box or implementing a custom command line interface.

### Installation
flair is on PyPI:

```
python -m pip install fl-flair
```

Alternatively you can install straight from this repository:

```sh
python -m pip install https://github.com/biqqles/flair/archive/master.zip
```

Built wheels are also available under [Releases](https://github.com/biqqles/flair/releases), as is a changelog. flair requires Python 3.6 or higher.

### Basic usage
flair must be run with administrator privileges. This is required for it to be able to hook keyboard input in Freelancer.

flair includes a testing mode. To access it run `python -m flair <path_to_freelancer>`. In this mode flair will load all built-in augmentations, print all events, and begin polling and printing the state of the game to the terminal. More on all of those later.

To use flair in your own programs, simply create an instance of `flair.FreelancerState`. This will begin polling the game (by default every 1 second). The polling frequency only affects when events are emitted - in most cases accesses to FreelancerState will cause the immediate state of the game to be read.

Basic usage of flair relies on two main principles:

 - a state object, which allows access to the game's state in real time
 - a simple events system inspired by Qt's signals and slots mechanism

The API for the hook itself is also of course available for cases not covered by the builtin `FreelancerState`, like creating [augmentations](#augmentations).

All these concepts are discussed in detail below.

## API
### FreelancerState
As mentioned earlier, simply create an instance of `flair.FreelancerState` to get access to the game state. Its constructor takes one argument, the path to the game's folder. This object has the following methods and properties:

|Methods             |Type             |Notes                                                                                    |
|:-------------------|:----------------|:----------------------------------------------------------------------------------------|
|`begin_polling(period)`|              |Begin polling the game's state and emitting events. Called upon instantiation by default.|
|`stop_polling()`    |                 |Stop polling the game's state and emitting events.                                       |
|`refresh()`         |                 |Cause state variables to refresh themselves                                              |
|**Properties**      |**Type**         |**Notes**                                                                                |
|**`running`**       |`bool`           |Whether an instance of the game is running                                               |
|**`foreground`**    |`bool`           |Whether an instance of the game is in the foreground and accepting input                 |
|**`chat_box`**      |`bool`           |Whether the chat box is open                                                             |
|**`account`**       |`str`            |The "name" (hash) of the currently active account, taken from the registry               |
|**`mouseover`**     |`str`            |See documentation in hook/process.                                                       |
|**`character_loaded`**|`bool`         |Whether a character is currently loaded (i.e. the player is logged in), either in SP or MP|
|**`name`**          |`Optional[str]`  |The name of the currently active character if there is one, otherwise None               |
|**`credits`**       |`Optional[int]`  |The number of credits the active character has if there is one, otherwise None           |
|**`system`**        |`Optional[str]`  |The display name (e.g. "New London") of the system the active character is in if there is one, otherwise None|
|**`base`**          |`Optional[str]`  |The display name (e.g. "The Ring") of the base the active character last docked at if there is one, otherwise None|
|**`pos`**           |`Optional[PosVector]`|The position vector of the active character if there is one, otherwise None          |
|**`docked`**        |`Optional[bool]` |Whether the active character is presently docked at a base if there is one, otherwise None|

Source: [flair/inspect/state.py](flair/inspect/state.py)

### Events
Events are used by "connecting" them to functions (or vice-versa). flair automatically "emits" these events when necessary. For example `flair.events.message_sent.connect(lambda message: print(message))` causes that lambda to be called every time flair emits the `message_sent` signal, thereby printing the contents of the message to the terminal.
 
|Event                       |Emitted when                       | Parameter(s)                                                  |
|:---------------------------|:----------------------------------|:--------------------------------------------------------------|
|**`character_changed`**     |New character loaded               |`name`=new character name                                      |
|**`account_changed`**       |Active (registry) account changed  |`account`=new account code                                     |
|**`system_changed`**        |New system entered                 |`system`=New system display name                               |
|**`docked`**                |Docked base (respawn point) changed|`base`=new base display name                                   |
|**`undocked`**              |Undocked from base                 |N/A                                                            |
|**`credits_changed`**       |Credit balance changed             |`balance`=new credit balance                                   |
|**`message_sent`**          |New message sent by player         |`message`=message text                                         |
|**`chat_box_opened`**       |Chat box opened                    |`message`=message text                                         |
|**`chat_box_closed`**       |Chat box closed                    |`message_sent`=whether message sent                            |
|**`freelancer_started`**    |Freelancer process launched        |N/A                                                            |
|**`freelancer_stopped`**    |Freelancer process closed          |N/A                                                            |
|**`switched_to_foreground`**|Freelancer switched to foreground  |N/A                                                            |
|**`switched_to_background`**|Freelancer switched to background  |N/A                                                            |

Source: [flair/inspect/events.py](flair/inspect/events.py)

### Hook
[`flair/hook`](flair/hook) contains the lower-level code for hooking into the game. You will likely only need to use this directly if you wish to go beyond simply using `FreelancerState` and the events system. It is separated into the following modules:

#### Input
Source: [flair/hook/input](flair/hook/input)

##### `bind_hotkey(combination, function)`
Adds a hotkey which is only active when Freelancer is in the foreground.

##### `unbind_hotkey(combination, function)`
Removes a hotkey that has been bound in the Freelancer window.

##### `queue_display_text(text: str)`
Queue text to be displayed to the user. If Freelancer is in the foreground and the chat box is closed,
this will be shown immediately. Otherwise, the text will be shown as soon as both these conditions are true.

##### `send_message(message: str, private=True)`
Inserts `message` into the chat box and sends it. If `private` is true, send to the Console.

##### `inject_keys(key: str, after_delay=0.0)`
Inject a key combination into the Freelancer window.

##### `inject_text(text: str)`
Inject text into the chat box.

##### `initialise_hotkey_hooks()`
Initialise hotkey hooks for Freelancer. Should be run when, and only when, the Freelancer window is brought into
the foreground.

##### `terminate_hotkey_hooks()`
Release hotkey hooks for Freelancer. Should be run when, and only when, the Freelancer window is put into the
background.

##### `on_chat_box_opened()`
Handle the user opening the chat box. Emits the `chat_box_opened` signal.

##### `on_chat_box_closed(cancelled=False)`
Handle the user closing the chat box. Emits the `chat_box_closed` signal.

##### `collect_chat_box_events(event)`
Handle a keyboard event while the chat box is open.
# Todo: handle arrow keys, copy and paste

##### `get_chat_box_contents()`
Return (our best guess at) the current contents of the chat box. If it is closed, returns a blank string.

##### `get_chat_box_open_hotkey()`
Return the hotkey configured to open the chat box.

#### Process
Source: [flair/hook/process](flair/hook/process)##### `get_process() -> <built-in function HANDLE>`
Return a handle to Freelancer's process.

##### `read_memory(process, address, datatype, buffer_size=128)`
Reads Freelancer's process memory.

Just as with string resources, strings are stored as UTF-16 meaning that the end of a string is marked by two
consecutive null bytes. However, other bytes will be present in the buffer after these two nulls since it is of
arbitrary size, and these confuse Python's builtin .decode and result in UnicodeDecodeError. So we can't use it.

##### `get_value(process, key, size=None)`
Read a value from memory. `key` refers to the key of an address in `READ_ADDRESSES`

##### `get_string(process, key, length)`
Read a UTF-16 string from memory.

##### `get_name(process) -> str`
Read the name of the active character from memory.

##### `get_credits(process) -> int`
Read the credit balance of the active character from memory.

##### `get_position(process) -> Tuple[float, float, float]`
Read the position of the active character from memory.

##### `get_mouseover(process) -> str`
This is a really interesting address. It seems to store random, unconnected pieces of text that have been
recently displayed or interacted with in the game. These range from console outputs to the names of bases
and planets immediately upon jumping in or docking, to the prices of commodities in the trader screen, to
mission "popups" messages, to the name of some solars and NPCs that are moused over while in space.
With some imagination this can probably be put to some use...

##### `get_rollover(process) -> str`
Similar to mouseover, but usually contains tooltip text.

##### `get_last_message(process) -> str`
Read the last message sent by the player from memory

##### `get_chat_box_state(process) -> bool`
Read the state of the chat box from memory.

##### `get_character_loaded(process) -> bool`
Read whether a character is loaded (whether in SP or MP).

##### `get_docked(process) -> bool`
Read whether the active character is docked.

#### Window
Source: [flair/hook/window](flair/hook/window)##### `get_hwnd() -> int`
Returns a non-zero window handle to Freelancer if a window exists, otherwise, returns zero.

##### `is_present() -> bool`
Reports whether Freelancer is running.

##### `is_foreground() -> bool`
Reports whether Freelancer is in the foreground and accepting input.

##### `get_screen_coordinates()`
Return the screen coordinates for the contents ("client"; excludes window decorations) of a Freelancer window.

##### `make_borderless()`
Remove the borders and titlebar from the game running in windowed mode.
Todo: Windowed mode seems to cut off the bottom of the game. This is something that will need worked around.

#### Storage
Source: [flair/hook/storage](flair/hook/storage)##### `get_active_account_name() -> str`
Returns the currently active account's code ("name") from the registry.
Note that Freelancer reads the account from the registry at the time of server connect.

##### `virtual_key_to_name(vk) -> str`
Get the name of a key from its VK (virtual key) code.

##### `get_user_keymap() -> Dict[str, str]`
Get Freelancer's current key map as defined in UserKeyMap.ini, in a format understood by the `keyboard`
module.

##### `tail_chat_log()`
(Discovery only)
Get the last message recorded in DSAce.log

##### `get_launcher_accounts() -> Dict[str, Tuple[str, str]]`
(Discovery only)
Parse launcheraccounts.xml to a dictionary of tuples of the form {code: (name, description)}.

### Augmentations
"Augmentations" are modules that augment the game client. flair includes several such built-in example modules.

To create an augmentation, subclass `flair.augment.Augmentation`. Simply override the methods `load()` and `unload()`. These are run when augmentations are "loaded" into the game client and "unloaded" respectively. Connect up the events you need to use and add any other setup here.

Source: [flair/augment](flair/augment)

#### Clipboard
Adds clipboard access to the chat box. Use Ctrl+Shift+C to copy the contents of the chat box and Ctrl+Shift+V to paste text to it.

#### CLI
Adds a basic command-line interface to the game.
If you are on a vanilla server you will need to type commands into the console (press ↑ in the chat box). This is not necessary on a server running FLHook as it will recognise them as commands and not send them to other players. Output is returned in chat, again through the console.

- `date`: print the local date and time
- `sector`: print the current sector and system
- `eval`: evaluate the given expression with Python
- `quit`: quit the game
- `help`: show this help message

#### Screenshot
Adds proper screenshot functionality to the game, similar to that found in games like *World of Warcraft*. Screenshots are automatically named with a timestamp and the system name and saved to `My Games/Freelancer/Screenshots` with the character name as the directory. Screenshots are taken using Ctrl+PrintScreen.

### To do
- Reimplementing Wizou's multiplayer code
- Increasing the robustness of determining the chat box contents - currently it does not handle arrow keys
- Getting system and base is currently pretty hacky, and it often requires a dock and undock to set both after loading a character
