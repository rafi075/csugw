import argparse

"""
usage: demo.py [-h] [{GET,SET}] [tag] [value]

A program that handles GET and SET operations for tags.

positional arguments:
  {GET,SET}   Action to be performed.
              Can be either 'GET' or 'SET'.
  tag         Tag to be used.
  value       Value to be set. Only applicable if action is 'SET'.

optional arguments:
  -h, --help  show this help message and exit
"""

parser = argparse.ArgumentParser(
    description="A program that handles GET and SET operations for tags.",
    formatter_class=argparse.RawTextHelpFormatter,
)

parser.add_argument(
    "action",
    type=str,
    choices=["GET", "SET"],
    nargs="?",
    help="Action to be performed.\n" "Can be either 'GET' or 'SET'.",
)

# tag is a string value
parser.add_argument("tag", type=str, nargs="?", help="Tag to be used.")

# value is an optional integer
parser.add_argument(
    "value",
    type=int,
    nargs="?",
    help="Value to be set. Only applicable if action is 'SET'.",
)

args = parser.parse_args()
if args.action is None:
    print("No Args")
elif args.action == "GET":
    print(f"{args.tag}-GET-5")
elif args.action == "SET":
    if args.value is None:
        print("Invalid")
    else:
        print(f"{args.tag}-SET-{args.value}")
