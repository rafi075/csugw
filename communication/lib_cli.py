import re
import os
import time
from tabulate import tabulate
from colour import *
import json

try:
    size = os.get_terminal_size()
    MAX_WIDTH = size.columns - 10
except OSError:
    # Provide some defaults if running without a terminal
    MAX_WIDTH = 100


def get_user_input(prompt:str = "", sign: str = " >> ", _prompt_color: str = "cyan", _input_color: str = "yellow") -> str:
    """
    Summary
    -------------
    Prompt the user for input, with color support.

    Args
    -------------
        - `prompt` (`str`, `optional`): Message to describe the prompt purpose. Defaults to "".
        - `sign` (`str`, `optional`): Indicator for user input. Defaults to " >> ".
        - `_prompt_color` (`str`, `optional`): Prompt Color. Defaults to "cyan".
        - `_input_color` (`str`, `optional`): User Input Color. Defaults to "yellow".

    Returns
    -------------
        - `str`: The user input.

    Example
    -------------
    ```python
        age = get_user_input("What is your age?")
        print(age)
    ```
    >>> What is your age? >> 
    >>> 20
    """
    text = input(color(_prompt_color, prompt + sign) + color(_input_color, "", terminated=False))
    reset_color()
    return text

def process_input(user_input:str):
    from cli_commands import CLI_COMMANDS, CLI_DEFAULT_COMMANDS
    user_input = user_input.split(" ")
    for command in CLI_COMMANDS + CLI_DEFAULT_COMMANDS:
        if user_input[0] in command["Commands"]:
            if len(command["Parameters"]) > 0:
                return command["Function"](*command["Parameters"])
            elif len(user_input) > 0:
                return command["Function"](*user_input[1:])
            else:
                return command["Function"]()
    else:
        print(f"Command '{user_input}' not found.")


def input_loop():
    show_help_menu_brief()
    while True:
        user_input = get_user_input(prompt="CLI")
        if (process_input(user_input) == "break"):
            break

def create_menu(commands:list[dict], 
                headers = ["Commands", "Description"], 
                use_headers = False, 
                verbose=True, 
                pad = 40):
    
    # Prepare the data
    data = []
    for command in commands:
        row = {}
        for header in headers:
            p = int(pad / 2) if header == "Commands" else pad
            if isinstance(command[header], list):
                row[header] = ',    '.join(command[header]).ljust(p, '⠀')
            else:
                row[header] = str(command[header]).ljust(p, '⠀')
        data.append(row)

    # Create and print the table
    menu = tabulate(data, headers = "keys" if use_headers else [], tablefmt="rounded_grid")
    if verbose: print(menu)
    return menu

def create_help_menu(main_menu:list[dict], 
                     help_menu:list[dict], 
                     headers:list[str] = ["Commands", "Description"], 
                     verbose=True, 
                     pad = 70):
    
    message("Help Menu", width = (pad * (4/3)) + 20)
    m_menu = create_menu(main_menu, headers=headers, use_headers = True, verbose = verbose, pad = pad)
    h_menu = create_menu(help_menu, headers=headers, use_headers = False, verbose = verbose, pad = pad)
    return (m_menu, h_menu)

def show_help_menu():
    from cli_commands import CLI_COMMANDS, CLI_DEFAULT_COMMANDS
    create_help_menu(CLI_COMMANDS, CLI_DEFAULT_COMMANDS, pad=80)

def show_help_menu_brief():
    from cli_commands import CLI_COMMANDS, CLI_DEFAULT_COMMANDS
    create_menu([CLI_DEFAULT_COMMANDS[0]], use_headers = False, pad = 80)

def bold(string: str) -> str:
    """
    Makes a string bold.

    Args
    -------------
        - `string` (str): The string to be made bold.

    Returns
    -------------
        `str`: The input string made bold using ANSI escape codes.

    Example
    -------------
    ```python
    bold("Hello, World!")
    ```
    >>> "\033[1mHello, World!\033[0m"

    Note:
        The function makes use of ANSI escape codes. These codes might not work as expected in non-ANSI-compatible environments.
    """
    return f"\033[1m{string}\033[0m"

def underline(string: str) -> str:
    """
    Underlines a string.

    Args
    -------------
        - `string` (str): The string to be underlined.

    Returns
    -------------
        `str`: The input string underlined using ANSI escape codes.

    Example
    -------------
    ```python
    underline("Hello, World!")
    ```
    >>> "\033[4mHello, World!\033[0m"

    Note:
        The function makes use of ANSI escape codes. These codes might not work as expected in non-ANSI-compatible environments.
    """
    return f"\033[4m{string}\033[0m"

def reset_color():
    print("\033[0m", end="")

def color(color: str, string: str, terminated:bool = True) -> str:
    """
        Applies color to a string.

    Args
    -------------
        - `color` (str): The color to be applied. It should be a valid color name or color code.
        - `string` (str): The string to be colored.
        - `terminated` (bool, optional): If True, the default color will be restored at the end of the string. Defaults to True.


    Returns
    -------------
        `str`: The input string colored with the provided color.

    Example
    -------------
    ```python
    color("#FF0000", "Hello, World!")
    color("red", "Hello, World!")
    ```
    >>> "<colored string>"

    Note
    -------------
    This function uses the rgb_to_ansi and _get_hex functions, 
    which are not included in this snippet.
    """
    return rgb_to_ansi(string, _get_hex(Color(color)), terminated)

def line(length:int = MAX_WIDTH, verbose:bool = False) -> str:
    """
    Formats a line.

    Args
    -------------
        - `length` (int, optional): The length of the line. Defaults to MAX_WIDTH.
        - `verbose` (bool, optional): If set to a truth, the output will be printed to the 
            console. Otherwise, it will be returned as a string. Defaults to False.

    Returns
    -------------
        `str`: The formatted line as a string, if `verbose` is False.

    Example
    -------------
    ```python
        PrintUtil.line(verbose=True)
    ```
    >>> ────────────────────────────────────────────────────
    """
    content = "─" * length
    if verbose:
        print(content)
    return content

def message(text: str, width: int = round(MAX_WIDTH/2), verbose: bool = True, **kwargs):
    """
    Creates a centered message inside a box with a specified width.

    Args
    -------------
        - `text` (str): The message text to be centered.
        - `width` (int, optional): The total width of the box. The message text will be centered within this width. Defaults to half of MAX_WIDTH.
        - `verbose` (bool, optional): If set to True, the function will print the output. 
            Otherwise, it will just return the string without printing. Defaults to True.
        - `**kwargs`: Arbitrary keyword arguments for the `tabulate` function.

    Returns
    -------------
        `str`: The formatted message as a string.

    Example
    -------------
    ```python
    message("Hello, World!", width = 20, verbose = True)
    ```
    >>> ╭──────────────────────────╮
    >>> │ <    Hello, World!     > │
    >>> ╰──────────────────────────╯

    Note
    -------------
    This function uses the `tabulate` function, which is not included in this snippet. 
    `tabulate` should be imported from the `tabulate` module before using this function.
    """
    _width = round((width - len(text))/2) - 3
    msg = tabulate([[f"<{'':>{_width}}{text}{'':<{_width}} >"]], tablefmt='rounded_grid', **kwargs)
    if verbose:
        print(msg)
    return "\n" + msg


def table(data: list or dict, headers:list = None, verbose:bool = True, ansi=False, indent_level:int = 0, **kwargs):
    """
    Formats a list or dictionary into a well-structured table.

    Args
    -------------
        - `data` (list || dict): The list or dictionary to be converted into a table.
        - `headers` (list, optional): The headers for the table columns. If not specified, it is generated from the keys of the dictionaries in `data` (for dict data) or from the first element of `data` (for list data). Defaults to [].
        - `verbose` (bool, optional): If True, the function will print the table. Otherwise, it will only return the table as a string. Defaults to True.
        - `ansi` (bool, optional): If True, the table will be colored using ANSI escape codes. Defaults to False.
        - `indent_level` (int, optional): The number of indentations for the printed table. Each indentation level corresponds to one tab character. Defaults to 0.
        - `**kwargs`: Additional keyword arguments for the `tabulate` function.

    Returns
    -------------
    `str`: The formatted table as a string.

    Example
    -------------
    ```python
    data = [
        {'name': 'Alice', 'age': 25},
        {'name': 'Bob', 'age': 30}
    ]
    table(data, verbose=True)
    ```
    >>> ╭───────┬────────╮
    >>> │   age │ name   │
    >>> ├───────┼────────┤
    >>> │    25 │ Alice  │
    >>> ├───────┼────────┤
    >>> │    30 │ Bob    │
    >>> ╰───────┴────────╯
    
    ```python
    data = {
        "days": [
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            [1, 2, 3, 4, 5, 6, 7],
            [8, 9, 10, 11, 12, 13, 14]
        ]
    }
    table(data["days"], verbose=True)
    ```
    >>> ╭───────┬───────┬───────┬───────┬───────┬───────┬───────╮
    >>> │   Mon │   Tue │   Wed │   Thu │   Fri │   Sat │   Sun │
    >>> ├───────┼───────┼───────┼───────┼───────┼───────┼───────┤
    >>> │     1 │     2 │     3 │     4 │     5 │     6 │     7 │
    >>> ├───────┼───────┼───────┼───────┼───────┼───────┼───────┤
    >>> │     8 │     9 │    10 │    11 │    12 │    13 │    14 │
    >>> ╰───────┴───────┴───────┴───────┴───────┴───────┴───────╯
    
    Note
    -------------
        This function uses the `tabulate` function, which should be imported from the `tabulate` module before using this function.
    """
    array = []
    if isinstance(data, dict) or isinstance(data[0], dict) :
        if headers is None:
            headers = sorted(set(key for d in data for key in d))

        for d in data:
            d = ((h, d.get(h, '-')) for h in headers)

        array = [[d[h] for h in headers] for d in data]

    else:
        if data and not isinstance(data[0], list):
            array = [data]
        else:
            # headers = headers or data[0]
            array = data

    if headers is not None:
        headers = [underline(bold(h)) if ansi else h for h in headers]
    else:
        headers = ()

    msg = tabulate(array, headers=headers, tablefmt='rounded_grid', **kwargs)
    msg = "\n".join("\t"*indent_level+line for line in msg.split("\n"))

    if verbose:
        print(msg)
    return msg

def print_array(data: list, indentation_level: int = 0):
    """
    Pretty prints an array with specified indentation.

    Args
    -------------
        - `data` (list): The array to be printed.
        - `indentation_level` (int, optional): The number of indentations for the print statement. Defaults to 0.

    Example
    -------------
    ```python
    print_array([1, 2, 3], indentation_level=1)
    ```
    >>> [
    >>>     1,
    >>>     2,
    >>>     3
    >>> ]
    """
    print(indent(json.dumps(data, indent=4), level=indentation_level))

def print_dict(data: dict, indentation_level: int = 0):
    """
    Pretty prints a dictionary with specified indentation.

    Args
    -------------
        - `data` (dict): The dictionary to be printed.
        - `indentation_level` (int, optional): The number of indentations for the print statement. Defaults to 0.

    Example
    -------------
    ```python
    print_dict({'a': 1, 'b': 2}, indentation_level=1)
    ```
    >>> {
    >>>     "a": 1,
    >>>     "b": 2
    >>> }
    """
    print(indent(json.dumps(data, indent=4), level=indentation_level))

def clear_terminal():
    """
    Clears the terminal screen.

    Example
    -------------
    ```python
    clear_terminal()
    ```
    The terminal screen will be cleared.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def rgb_to_ansi(text, c:str, terminated:bool = True):
    """
    Converts RGB color to the nearest equivalent ANSI color and applies it to a text string.

    Args
    -------------
        - `text` (str): The string to be colored.
        - `c` (str): The RGB color code in hex format (without the '#' symbol).
        - `terminated` (bool, optional): If True, the default color will be restored at the end of the string. Defaults to True.

    Returns
    -------------
        `str`: The input string colored with the provided RGB color code.

    Example
    -------------
    ```python
    rgb_to_ansi("Hello, World!", "FF0000")
    ```
    >>> Output will be 'Hello, World!' colored in red in a terminal supporting ANSI colors.
    """

    r = int(c[0:2], base=16)
    g = int(c[2:4], base=16)
    b = int(c[4:6], base=16)
    # Calculate grey value
    grey_possible = (r < 8) or (g < 8) or (b < 8) or (r > 248) or (g > 248) or (b > 248)
    grey_id = 232
    if grey_possible:
        if abs(r - g) <= 10 and abs(r - b) <= 10 and abs(g - b) <= 10:
            grey_id = round(((r * 0.299 + g * 0.587 + b * 0.114) - 8) / 247 * 24)
            return 232 + grey_id

    # Convert RGB to 6 cube range
    ansi_r = round(r / 255 * 5)
    ansi_g = round(g / 255 * 5)
    ansi_b = round(b / 255 * 5)

    return f"\033[38;5;{(16 + (36 * ansi_r) + (6 * ansi_g) + ansi_b)}m{text}" + ("\033[0m" if terminated else "")

def timer(func):
    """
    A decorator that prints the time a function takes to execute.

    Args
    -------------
        - `func` (Callable): The function to be timed.

    Returns
    -------------
        `Callable`: The decorated function, which will print its execution time when called.

    Example:
        ```python
        @timer
        def my_function(x):
            # Some time-consuming operations...
        ```
        When `my_function` is called, it will also print the time it took to execute.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(color("cyan", f"RUNTIME [ {func.__name__} ] {round(end_time - start_time, 4):>30} second(s)"))
        return result
    return wrapper

def _get_hex(color: Color):
    """
    Converts a Color object to a hex color code.

    Args
    -------------
       - `color` (Color): A color object.

    Returns
    -------------
        `str`: The hex color code corresponding to the input Color object.

    Note
    -------------
        This function expects 'color' to be an instance of a `Color` class which is imported from the `colour` module.
    """
    he = color.get_hex()[1:]
    if len(he) == 3:
        he = he[0] + he[0] + he[1] + he[1] + he[2] + he[2]
    return he


def indent(text: str, level: int = 0) -> str:
    """
    Indents a text string by a specified number of levels.

    Args
    -------------
        - `text` (str): The string to be indented.
        - `level` (int, optional): The number of indentation levels. Each level corresponds to one tab character. Defaults to 0.

    Returns
    -------------
        `str`: The indented string.

    Example
    -------------
    ```python
    _indent("Hello, World!", level=1)
    ```
    >>> "\tHello, World!"
    """
    msg = ""
    for line in text.split("\n"):
        msg += "\t"*level + line + "\n"
    return msg