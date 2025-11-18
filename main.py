import csv
import sys
from collections import defaultdict

try:
    import readline
except ImportError:
    pass

import core
from man import render_help


STORE_PATH = "store.bin"
CONFIG_PATH = "config.json"
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
    "sort-by-tags": (0, 0),
    "find-notes": (1, 1),
    "tag": (1, 3),
    "encryption": (1, 1),
    "skip": (0, 0),
}

CMD_SYNONYMS = {
    "exit": ["quit", "bye", "close"],
    "hello": ["hi"],
    "help": ["man"],
    "new-record": ["new", "create", "touch"],
    "new-note": ["new", "create", "touch"],
    "records": ["all", "show", "rename", "delete", "person", "contact", "people"],
    "notes": ["all", "show", "update", "delete", "text"],
    "phone": ["number"],
    "address": ["city", "street", "town", "country", "house"],
    "email": [],
    "birthday": [],
    "photo": ["image", "avatar", "picture"],
    "birthdays": ["congratulate"],
    "find-records": ["search", "filter"],
    "find-notes": ["search", "filter"],
    "tag": ["keyword"],
    "encryption": ["privacy", "crypto"],
    "sort-by-tags": ["category"],
}


def guess_cmd(cmd: str) -> list:
    if len(set(cmd)) < 3:
        return []

    all_sigs = defaultdict(list)
    all_sig_names = {}
    for real in CMD_SYNONYMS:
        all_sigs[frozenset(real)].append(real)
        all_sig_names[frozenset(real)] = real
        for syn in CMD_SYNONYMS[real]:
            all_sigs[frozenset(syn)].append(real)
            all_sig_names[frozenset(syn)] = syn

    match_scores = []
    input_sig = set(cmd)
    for sig, cmds in all_sigs.items():
        match_score = len(input_sig.intersection(sig))
        match_scores.append((match_score, tuple(cmds), all_sig_names[sig]))

    match_scores.sort(reverse=True)
    return [{"input": score[2], "cmds": score[1]} for score in match_scores if score[0] > 2]


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
        suggestions = guess_cmd(cmd)
        if not suggestions:
            raise ValueError("Unknown command.")
        candidate = suggestions[0]
        if candidate["input"] not in candidate["cmds"]:
            print(f"You probably wanted to type `{suggestions[0]["input"]}`, but such command doesn't exist.")
            print(f"Similar commads: {", ".join(candidate["cmds"])}")
        else:
            print(f"Did you mean typing: {", ".join(candidate["cmds"])}?")
        cmd = "skip"

    if not CMD_CFG[cmd][0] <= len(input_args) <= CMD_CFG[cmd][1]:
        raise ValueError(MSG_BAD_ARG_COUNT)

    args[:len(input_args)] = input_args
    return cmd, args


def main():
    if len(sys.argv) == 1:
        print("Welcome to the assistant bot!\nType `help` to learn more about available commands.")
    data = core.load_store(STORE_PATH, CONFIG_PATH)
    if data is None:
        sys.exit(1)

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
        "encryption": core.handle_encryption,
        "sort-by-tags": core.handle_sort_by_tags,
    }

    while True:
        # Handle empty input, interrupts and parse errors
        try:
            if len(sys.argv) == 1:
                cmd = input("> ")
            else:
                cmd = " ".join(sys.argv[1:])
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
                print(core.save_store(data, STORE_PATH, CONFIG_PATH))
                print("Exiting program. Good bye!")
                break
            case "hello":
                print("Hello! How can I help you?")
            case "help":
                print(render_help())
            case "new-record" | "records" | "birthdays" | "find-records" | "phone":
                print(cmd_funcs[cmd](args, data["book"]))
                core.save_store(data, STORE_PATH, CONFIG_PATH)
            case "address" | "email" | "birthday" | "photo":
                print(cmd_funcs[cmd](cmd, args, data["book"]))
                core.save_store(data, STORE_PATH, CONFIG_PATH)
            case "new-note" | "notes" | "find-notes" | "tag" | "sort-by-tags":
                print(cmd_funcs[cmd](args, data["notebook"]))
                core.save_store(data, STORE_PATH, CONFIG_PATH)
            case "encryption":
                print(cmd_funcs[cmd](args, data["config"]))
                core.save_store(data, STORE_PATH, CONFIG_PATH)
            case "skip":
                continue
            case _:
                print("ERROR: Unknown command. Try again.")
        if len(sys.argv) > 1:
            break

if __name__ == "__main__":
    main()
