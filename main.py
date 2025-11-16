import csv
try:
    import readline
except ImportError:
    pass

import core
from contacts import AddressBook
from prettytable import PrettyTable

FILEPATH = "addressbook.pkl"

def get_help_message() -> str:
    """Generate formatted help message using PrettyTable."""
    table = PrettyTable()
    table.field_names = ["Command", "Description"]
    table.align["Command"] = "l"
    table.align["Description"] = "l"
    table.max_width["Description"] = 50
    
    # Record commands
    table.add_row(["=== RECORD MANAGEMENT ===", ""])
    table.add_row(["record <name>", "Show or create Record"])
    table.add_row(["record <name> <new_name>", "Rename Record"])
    table.add_row(["record <name> \"\"", "Delete Record"])
    
    # Record properties
    table.add_row(["", ""])
    table.add_row(["=== RECORD PROPERTIES ===", ""])
    table.add_row(["address <name>", "Show address"])
    table.add_row(["address <name> <value>", "Set address"])
    table.add_row(["address <name> \"\"", "Unset address"])
    table.add_row(["birthday <name>", "Show birthday (DD.MM.YYYY)"])
    table.add_row(["birthday <name> <value>", "Set birthday"])
    table.add_row(["birthday <name> \"\"", "Unset birthday"])
    table.add_row(["email <name>", "Show email"])
    table.add_row(["email <name> <value>", "Set email"])
    table.add_row(["email <name> \"\"", "Unset email"])
    
    # Phone management
    table.add_row(["", ""])
    table.add_row(["=== PHONE MANAGEMENT ===", ""])
    table.add_row(["phone <name>", "Show all phones"])
    table.add_row(["phone <name> <number>", "Add phone (10 digits, starts with 0)"])
    table.add_row(["phone <name> <old> <new>", "Replace phone number"])
    table.add_row(["phone <name> <number> \"\"", "Delete phone"])
    
    # Search and view
    table.add_row(["", ""])
    table.add_row(["=== SEARCH & VIEW ===", ""])
    table.add_row(["all", "Show all Records"])
    table.add_row(["all <name>", "Show specific Record"])
    table.add_row(["find <keyword>", "Search Records by keyword"])
    table.add_row(["birthdays [<days>]", "Show upcoming birthdays (default: 7 days)"])
    
    # System commands
    table.add_row(["", ""])
    table.add_row(["=== SYSTEM ===", ""])
    table.add_row(["hello", "Print greeting"])
    table.add_row(["help", "Show this message"])
    table.add_row(["exit | close", "Save and quit"])
    
    # Photo management
    table.add_row(["", ""])
    table.add_row(["=== PHOTO MANAGEMENT ===", ""])
    table.add_row(["photo <name>", "Show Record's photo"])
    table.add_row(["photo <name> <value>", "Set Record's photo (filepath or URL)"])
    table.add_row(["photo <name> \"\"", "Unset Record's photo"])

    # Notes collection actions:
    table.add_row(["", ""])
    table.add_row(["=== NOTES MANAGEMENT ===", ""])
    table.add_row(["notes", "Show all Notes with IDs"])
    table.add_row(["notes <id>", "Show Note"])
    table.add_row(["notes <id><val>", "Update Note"])
    table.add_row(["notes <id> \"\"", "Delete Note"])
    
    # Note list actions:
    table.add_row(["", ""])
    table.add_row(["=== Supported lists: tag ===", ""])
    table.add_row(["<list> <note_id>", "Show all list items"])
    table.add_row(["<list> <note_id> <val>", "Add new item to the list"])
    table.add_row(["<list> <note_id> <val> <new_val>", "Replace item with new value"])
    table.add_row(["<list> <note_id> <val> \"\"", "Delete item from the list"])

    output = "CLI for Contact Management\n\n"
    output += "NOTE: Use double quotes for values with spaces.\n\n"
    output += str(table)
    return output

MSG_HELP = get_help_message()

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
