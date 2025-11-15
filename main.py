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
    - add <person> <value>
        Add phone number for the specified person. Create person if missing.
    - change <person> <old_value> <new_value>
        Replace specified phone number with new value for the specified person.
    - phone <person>
        Print all person's phone numbers.
    - all [ <person> ]
        If person is specified, print person's fields table.
        Otherwise prints fields table for everyone.
    - add-birthday <person> <value>
        Add birthday for the specified person. Create person if missing.
    - show-birthday <person>
        Print person's birthday.
    - birthdays [ <days> ]
        If days is specified, print list of congratulation dates for persons which birthdays are \
        within specified period. Otherwise period defaults to 7 days.
    - help
        Prints this message.
    - hello
        Prints "hello" message.
    - exit | close
        Quits application.

NOTES:
    Person name can contain spaces."""

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
        "all": core.render_record_table,
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
