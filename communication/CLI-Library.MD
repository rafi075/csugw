# README.md

This Python utility provides several functions to help you with text formatting in the terminal. It also includes some utilities for terminal management. The utility uses ANSI escape codes, so these functions might not work as expected in non-ANSI-compatible environments. 

## Prerequisites
The following packages are used in this utility:
- `re`
- `os`
- `time`
- `tabulate`
- `colour`
- `json`

Make sure you have installed these packages before using the utility. You can install them using pip:
```bash
pip3 install tabulate colour
```

# Usage
- `bold()`
  
    The bold() function makes a string bold.
    
    ```python
    bold("Hello, World!")
    ```
    This will return the string "Hello, World!" made bold using ANSI escape codes.

- `underline()`
  
    The underline() function underlines a string.
    
    ```python
    underline("Hello, World!")
    ```
    This will return the string "Hello, World!" underlined using ANSI escape codes.

- `color()`
  
    The color() function applies a color to a string.
    
    ```python
    color("#FF0000", "Hello, World!")
    color("red", "Hello, World!")
    ```
    This will return the string "Hello, World!" colored with the provided color. It uses the `rgb_to_ansi` and `_get_hex` functions.

- `line()`
  
    The line() function formats a line.
    
    ```python
    line(verbose=True)

    >>> ──────────────────────────────────────────────────────
    ```
    This will print a line in the console.
    
- `message()`
  
    The message() function creates a centered message inside a box with a specified width.
    
    ```python
    message("Hello, World!", width = 20, verbose = True)

    >>> ╭──────────────────────────╮
    >>> │ <    Hello, World!     > │
    >>> ╰──────────────────────────╯
    ```
    This will print the message "Hello, World!" centered inside a box with a total width of 20 characters.
    
- `table()`
  
    The table() function formats a list or dictionary into a well-structured table.
    
    ```python
    data = [
        {'name': 'Alice', 'age': 25},
        {'name': 'Bob', 'age': 30}
    ]
    table(data, verbose=True)

    >>> ╭───────┬────────╮
    >>> │   age │ name   │
    >>> ├───────┼────────┤
    >>> │    25 │ Alice  │
    >>> ├───────┼────────┤
    >>> │    30 │ Bob    │
    >>> ╰───────┴────────╯
    ```
    This will print a table with the data from the data variable.

     ```python
    data = {
        "days": [
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            [1, 2, 3, 4, 5, 6, 7],
            [8, 9, 10, 11, 12, 13, 14]
        ]
    }
    table(data["days"], verbose=True)

    >>> ╭───────┬───────┬───────┬───────┬───────┬───────┬───────╮
    >>> │   Mon │   Tue │   Wed │   Thu │   Fri │   Sat │   Sun │
    >>> ├───────┼───────┼───────┼───────┼───────┼───────┼───────┤
    >>> │     1 │     2 │     3 │     4 │     5 │     6 │     7 │
    >>> ├───────┼───────┼───────┼───────┼───────┼───────┼───────┤
    >>> │     8 │     9 │    10 │    11 │    12 │    13 │    14 │
    >>> ╰───────┴───────┴───────┴───────┴───────┴───────┴───────╯   
    ```

- `print_array()`
  
    The print_array() function pretty prints an array with specified indentation.
    
    ```python
    print_array([1, 2, 3], indentation_level=1)
    >>> [
    >>>     1,
    >>>     2,
    >>>     3
    >>> ]
    ```
    This will print an array with each element on a new line, indented one level.

- `print_dict()`
      
    The print_dict() function pretty prints a dictionary with specified indentation.
    
    ```python
    print_dict({'a': 1, 'b': 2}, indentation_level=1)
    >>> {
    >>>     "a": 1,
    >>>     "b": 2
    >>> }
    ```
    This will print a dictionary with each key-value pair on a new line, indented one level.
    
- `clear_terminal()`
  
    The clear_terminal() function clears the terminal screen.
    
    ```python
    clear_terminal()
    ```
    This will clear the terminal screen.

    
- `timer()`
  
    The timer() decorator prints the time a function takes to execute.
    
    ```python
    @timer
    def my_function(x):
        # Some time-consuming operations...
    ```
    When my_function is called, it will also print the time it took to execute.
    ```python 
    @timer
    def temp_test(n):
        time.sleep(n)
        return "Done"

    result = temp_test(5)

    >>> RUNTIME [ temp_test ]                          5.004 second(s)
    ```

