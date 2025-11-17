import csv
try:
    import readline
except ImportError:
    pass

import core

STORE_PATH = "store.bin"
MSG_HELP = """\
DESCRIPTION:
    This script provides CLI for contact management.

USAGE:
  ##### Object creations:
    - new-record <name> : Create new Record.
    - new-note <val> : Create new Note.

  ##### Records collection actions:
    - records              : Show "cards" for all Records.
    - records <name>       : Show Record "card".
    - records <name> <val> : Rename Record.
    - records <name> ""    : Delete Record.

  ##### Record property actions:
    Supported properties: address, birthday, email, photo.
    - <property> <rec_name>       : Show Record's property.
    - <property> <rec_name> <val> : Set Record's property.
    - <property> <rec_name> ""    : Unset Record's property.

  ##### Record list actions:
    Supported lists: phone.
    - <list> <rec_name>                 : Show all list items.
    - <list> <rec_name> <val>           : Add new item to the list.
    - <list> <rec_name> <val> <new_val> : Replace item with new value.
    - <list> <rec_name> <val> ""        : Delete item from the list.

  ##### Notes collection actions:
    - notes            : Show all Notes with IDs.
    - notes <id>       : Show Note.
    - notes <id> <val> : Update Note.
    - notes <id> ""    : Delete Note.

  ##### Note list actions:
    Supported lists: tag.
    - <list> <note_id>                 : Show all list items
    - <list> <note_id> <val>           : Add new item to the list.
    - <list> <note_id> <val> <new_val> : Replace item with new value.
    - <list> <note_id> <val> ""        : Delete item from the list.

  ##### Other actions:
    - find-records <val> : Search inside Record fields by keyword.
    - find-notes <val>   : Search inside Notes fields by keyword.
    - birthdays [ <days> ] : Show congratulation dates for persons which birthdays are within specified period (7 days by default).
    - help : Prints this message.
    - hello : Prints "hello" message.
    - exit | close : Saves data into the file and quits application.

NOTES:
    Use double quotes if values contain spaces."""

MSG_BAD_ARG_COUNT = "Wrong number of arguments. Type `help` to read about command usage."
CMD_CFG = {
    "exit": (0, 0),
    "close": (0, 0),
    "hello": (0, 0),
    "help": (0, 0),
    "new-record": (1, 1),
    "new-note": (1, 1),
    "records": (0, 2),
    "notes": (0, 2),
    "phone": (1, 3),
    "address": (1, 2),
    "email": (1, 2),
    "birthday": (1, 2),
    "photo": (1, 2),
    "birthdays": (0, 1),
    "find-records": (1, 1),
    "find-notes": (1, 1),
    "tag": (1, 3),
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
        raise ValueError("Unknown command.")

    if not CMD_CFG[cmd][0] <= len(input_args) <= CMD_CFG[cmd][1]:
        raise ValueError(MSG_BAD_ARG_COUNT)

    args[:len(input_args)] = input_args
    return cmd, args


def main():
    print("Welcome to the assistant bot!\nType `help` to learn more about available commands.")
    data = core.load_store(STORE_PATH)

    # Store functions for easier command handling
    cmd_funcs = {
        "new-record": core.handle_new_record,
        "new-note": core.handle_new_note,
        "records": core.handle_records,
        "notes": core.handle_notes,
        "phone": core.handle_phone,
        "address": core.handle_record_prop,
        "email": core.handle_record_prop,
        "birthday": core.handle_record_prop,
        "photo": core.handle_record_prop,
        "birthdays": core.handle_birthdays,
        "find-records": core.handle_find_records,
        "find-notes": core.handle_find_notes,
        "tag": core.handle_tag,
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
                print(core.save_store(data, STORE_PATH))
                print("Exiting program. Good bye!")
                break
            case "hello":
                print("Hello! How can I help you?")
            case "help":
                print(MSG_HELP)
            case "new-record" | "records" | "birthdays" | "find-records" | "phone":
                print(cmd_funcs[cmd](args, data["book"]))
                core.save_store(data, STORE_PATH)
            case "address" | "email" | "birthday" | "photo":
                print(cmd_funcs[cmd](cmd, args, data["book"]))
                core.save_store(data, STORE_PATH)
            case "new-note" | "notes" | "find-notes" | "tag":
                print(cmd_funcs[cmd](args, data["notebook"]))
                core.save_store(data, STORE_PATH)
            case _:
                print("ERROR: Unknown command. Try again.")


if __name__ == "__main__":
    main()
