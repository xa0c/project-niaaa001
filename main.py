import csv
import readline
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
    - birthdays
        Print list of congratulation dates for persons which birthdays occur in next 7 days.
    - help
        Prints this message.
    - hello
        Prints "hello" message.
    - exit | close
        Quits application.

NOTES:
    Person name can contain spaces."""

MSG_BAD_ARG_COUNT = "Wrong number of arguments. Type `help` to read about command usage."


def parse_input(user_input: str) -> tuple[str, dict[str, str]]:
    """Parse string into a tuple of command name and its arguments.

    Args:
        user_input (str): Input string.

    Returns:
        tuple[str, dict[str, str]]: Tuple of command name and a
            dictionary of it's arguments.

    Raises:
        ValueError: If user input has wrong number of arguments.
    """
    if not user_input:
        return "", {}

    reader = csv.reader([user_input.strip()], delimiter=" ")
    cmd, *args = next(reader)
    cmd = cmd.lower()
    match cmd:
        case "add" | "add-birthday":
            if len(args) != 2:
                raise ValueError(MSG_BAD_ARG_COUNT)
            args = {"name": args[0], "value": args[1]}
        case "change":
            if len(args) != 3:
                raise ValueError(MSG_BAD_ARG_COUNT)
            args = {"name": args[0], "old_value": args[1], "new_value": args[2]}
        case "phone" | "show-birthday":
            if len(args) != 1:
                raise ValueError(MSG_BAD_ARG_COUNT)
            args = {"name": args[0]}
        case "all":
            match len(args):
                case 0:
                    args = {"name": None}
                case 1:
                    args = {"name": args[0]}
                case _:
                    raise ValueError(MSG_BAD_ARG_COUNT)
        case "birthdays":
            if len(args) != 0:
                raise ValueError(MSG_BAD_ARG_COUNT)
            args = {}
    return cmd, args


def main():
    print("Welcome to the assistant bot!\nType `help` to learn more about available commands.")
    book = core.load_data(FILEPATH)

    # Store functions for easier command handling
    cmd_funcs = {
        "add": core.add_contact,
        "change": core.change_contact,
        "phone": core.show_phone,
        "all": core.render_record_table,
        "add-birthday": core.add_birthday,
        "show-birthday": core.show_birthday,
        "birthdays": core.birthdays,
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
            case (
                "add" | "change" | "phone" | "all" | "add-birthday" | "show-birthday" |
                "birthdays"
            ):
                print(cmd_funcs[cmd](args, book))
            case _:
                print("ERROR: Unknown command. Try again.")


if __name__ == "__main__":
    main()
