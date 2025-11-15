import csv
try:
    import readline
except ImportError:
    pass

import core
from contacts import AddressBook

FILEPATH = "addressbook.pkl"
MSG_HELP = """\
DESCRIPTION:
    This script provides CLI for contact management.

USAGE:
    - record <name>
        Show Record's "card". Create Record if missing.
    - record <record_name> <value>
        Rename Record.
    - record <record_name> ""
        Delete Record.

    - address <record_name>
        Show Record's address.
    - address <record_name> <value>
        Set Record's address.
    - address <record_name> ""
        Unset Record's address.
    - birthday <record_name>
        Show Record's birthday.
    - birthday <record_name> <value>
        Set Record's birthday.
    - birthday <record_name> ""
        Unset Record's birthday.
    - email <record_name>
        Show Record's email.
    - email <record_name> <value>
        Set Record's email.
    - email <record_name> ""
        Unset Record's email.

    - phone <record_name>
        Show all phones of the Record.
    - phone <record_name> <value>
        Add new phone to the Record.
    - phone <record_name> <value> <new_value>
        Replace phone with new value.
    - phone <record_name> <value> ""
        Delete phone from the list.

    - all [ <person> ]
        If person is specified, show Record "card".
        Otherwise show all "cards".
    - birthdays [ <days> ]
        If days is specified, show congratulation dates for persons which birthdays are within \
        specified period. Otherwise period defaults to 7 days.
    - help
        Prints this message.
    - hello
        Prints "hello" message.
    - exit | close
        Saves data into the file and quits application.

NOTES:
    Use double quotes if values contain spaces."""

MSG_BAD_ARG_COUNT = "Wrong number of arguments. Type `help` to read about command usage."
CMD_CFG = {
    "exit": (0, 0),
    "close": (0, 0),
    "hello": (0, 0),
    "help": (0, 0),
    "record": (1, 2),
    "phone": (1, 3),
    "address": (1, 2),
    "email": (1, 2),
    "birthday": (1, 2),
    "all": (0, 1),
    "birthdays": (0, 1),
    "find": (1, 1),
}


def parse_input(user_input: str) -> tuple[str, list[str]]:
    """Parse string into a tuple of command name and its arguments.

    Args:
        user_input (str): Input string.

    Returns:
        tuple[str, list[str]: Tuple of command name and arguments list.

    Raises:
        ValueError: If user input has wrong number of arguments.
    """
    if not user_input:
        return "", {}

    args = [None] * 3  # With `3` being the max number of args across all commands
    reader = csv.reader([user_input.strip()], delimiter=" ")
    cmd, *input_args = next(reader)
    cmd = cmd.lower()
    if cmd not in CMD_CFG:
        raise ValueError

    if not CMD_CFG[cmd][0] <= len(input_args) <= CMD_CFG[cmd][1]:
        raise ValueError(MSG_BAD_ARG_COUNT)

    args[:len(input_args)] = input_args
    return cmd, args


def main():
    print("Welcome to the assistant bot!\nType `help` to learn more about available commands.")
    book = core.load_data(FILEPATH)

    # Store functions for easier command handling
    cmd_funcs = {
        "record": core.handle_record,
        "phone": core.handle_phone,
        "address": core.handle_address,
        "email": core.handle_email,
        "birthday": core.handle_birthday,
        "all": core.handle_all,
        "birthdays": core.handle_birthdays,
        "find": core.handle_find,
    }

    while True:
        # Handle empty input, interrupts and parse errors
        try:
            cmd = input("> ")
            if not cmd:
                continue
            cmd, args = parse_input(cmd)
        except (KeyboardInterrupt, EOFError):
            print("\nProgram interrupted by user.")
            break
        except ValueError as e:
            print("ERROR:", e, "Try again.")
            continue

        # Handle commands
        match cmd:
            case "exit" | "close":
                core.save_data(book, FILEPATH)
                print("Exiting program. Good bye!")
                break
            case "hello":
                print("Hello! How can I help you?")
            case "help":
                print(MSG_HELP)
            case "record" | "phone" | "address" | "email" | "birthday" | "all" | "birthdays" | "find":
                print(cmd_funcs[cmd](args, book))
            case _:
                print("ERROR: Unknown command. Try again.")


if __name__ == "__main__":
    main()
