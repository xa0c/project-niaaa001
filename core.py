import functools
import json
import pickle
import re
from collections.abc import Callable

from cryptography.fernet import Fernet
from rich.console import Console
from rich.table import Table
from rich import box

from contacts import AddressBook, Record, InvalidPropertyFormatError
from notes import NoteBook, Note


class InvalidCmdArgsCountError(ValueError):
    """Custom exception for invalid cmd args count."""

    def __init__(self, message="Invalid cmd args count."):
        super().__init__(message)


class InvalidCmdArgTypeError(ValueError):
    """Custom exception for invalid cmd argument type."""

    def __init__(self, message="Invalid cmd argument data type."):
        super().__init__(message)


class RecordExistsError(ValueError):
    """Custom exception if specified Record exists."""

    def __init__(self, message="Specified Record already exists."):
        super().__init__(message)


class RecordNotExistsError(ValueError):
    """Custom exception if specified Record doesn't exist."""

    def __init__(self, message="Specified Record doesn't exist."):
        super().__init__(message)


class PhoneNotExistsError(ValueError):
    """Custom exception if specified Phone doesn't exist."""

    def __init__(self, message="Specified Phone doesn't exist."):
        super().__init__(message)


class NoteNotExistsError(ValueError):
    """Custom exception if specified Note doesn't exist."""

    def __init__(self, message="Specified Note doesn't exist."):
        super().__init__(message)


class TagNotExistsError(ValueError):
    """Custom exception if specified Tag doesn't exist."""

    def __init__(self, message="Specified Tag doesn't exist."):
        super().__init__(message)


def file_error(func: Callable) -> Callable:
    """Decorator for file error handling.

    Args:
        func (Callable): Function to wrap.

    Returns:
        Callable: Wrapped function with same signature.
    """
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FileNotFoundError, OSError) as e:
            return f"ERROR: {e.args[0]} Try again."
    return inner


def input_error(func: Callable) -> Callable:
    """Decorator that catches exceptions and returns them from function.

    Args:
        func (Callable): Function to wrap.

    Returns:
        Callable: Wrapped function with same signature.
    """
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (
            FileNotFoundError,
            InvalidCmdArgsCountError,
            InvalidCmdArgTypeError,
            InvalidPropertyFormatError,
            RecordExistsError,
            RecordNotExistsError,
            NoteNotExistsError,
            PhoneNotExistsError,
            TagNotExistsError,
        ) as e:
            return f"ERROR: {e.args[0]} Try again."
    return inner


@input_error
def handle_new_record(args: list[str], book: AddressBook) -> str:
    """Handle new-record command.

    Create new Record.

    Args:
        args (list[str]): List with raw cmd arguments.
            Expected: [name].
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        InvalidPropertyFormatError: If name format is invalid.
    """
    try:
        name, *_ = args
    except:
        raise InvalidCmdArgsCountError

    record = book.get_record(name)

    # Don't allow to overwrite existing Record
    if record is not None:
        raise RecordExistsError

    record = Record(name)
    book.add_record(record)
    return f"New `{name}` Record was created."


@input_error
def handle_records(args: list[str], book: AddressBook) -> str:
    """Handle record commands: all, show, rename, delete.

    If args is empty:
        Show "views" for all Records.
    If args has 1 item:
        Show "view" for specified Record.
    If args contains 2 items:
        Rename specified Record with the new value.
        If value is empty string, then delete specified Record.

    Args:
        args (list[str]): List with raw cmd arguments.
            Expected: [] or [name] or [name, value] or [name, ""].
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or Record "view".

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExistsError: If specified Record doesn't exist.
        InvalidPropertyFormatError: If new name format is invalid.
    """
    try:
        name, value, *_ = args
    except:
        raise InvalidCmdArgsCountError

    # Handle ShowAll functionality
    if name is None:
        return render_records("All Records", book) if book else "No Records."

    record = book.get_record(name)

    # If Record wasn't found, raise error for all cases except "ShowAll" functionality
    if record is None:
        raise RecordNotExistsError

    # Handle Show functionality
    if value is None:
        return render_records(str(record.name), {0: record})

    # Handle Delete functionality
    if value == "":
        book.delete_record(name)
        return f"Deleted `{name}` Record."

    # Handle Rename functionality
    book.rename_record(name, value)
    return f"Renamed `{name}` Record to `{value}`."


@input_error
def handle_phone(args: list[str], book: AddressBook) -> str:
    """Handle phone commands: show, add, replace, delete.

    If args has 1 item:
        Show all phones for the specified Record.
    If args has 2 items:
        Add phone to the specified Record.
    If args has 3 items:
        Replace specified phone with new value in specified Record.
        If new value is empty string, then delete specified phone.

    Args:
        args (list[str]): List with raw cmd arguments.
            Expected: [record_name] or [record_name, value] or
            [record_name, value, replace_value] or
            [record_name, value, ""].
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or phone numbers.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExistsError: If specified Record doesn't exist.
        PhoneNotExistsError: If specified phone doesn't exist.
        InvalidPropertyFormatError: If new phone format is invalid.
    """
    try:
        name, value, replace_value, *_ = args
    except:
        raise InvalidCmdArgsCountError

    record = book.get_record(name)

    # If Record wasn't found, raise error
    if record is None:
        raise RecordNotExistsError

    # Handle Get functionality
    if value is None:
        return render_phones(record)

    # Handle Add functionality
    if replace_value is None:
        if record.add_phone(value):
            return f"Added `{value}` phone to the `{name}` Record."
        else:
            return f"Skipped duplicate `{value}` phone in the `{name}` Record."

    # Check if specified phone field exists
    phone = record.find_phone(value)
    if phone is None:
        raise PhoneNotExistsError

    # Handle Delete functionality
    if replace_value == "":
        record.remove_phone(value)
        return f"Deleted `{value}` phone from the `{name}` Record."

    # Handle Update functionality
    phone.set_value(replace_value)
    return f"Replaced `{value}` phone to `{replace_value}` in the `{name}` Record."


@input_error
def handle_record_prop(prop: str, args: list[str], book: AddressBook) -> str:
    """Handle Record property commands: show, set, unset.

    If args has 1 item:
        Show property value of the specified Record.
    If args has 2 items:
        Set property of the specified Record.
        If new value is empty string, then unset property field.

    Args:
        args (list[str]): List with raw cmd arguments.
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or property text representation.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExistsError: If specified Record doesn't exist.
        InvalidPropertyFormatError: If property format is invalid.
    """
    try:
        name, value, *_ = args
    except:
        raise InvalidCmdArgsCountError

    record = book.get_record(name)

    # If Record wasn't found, raise error
    if record is None:
        raise RecordNotExistsError

    # Handle Get functionality
    if value is None:
        prop_val = getattr(record, prop)
        if prop_val is None:
            return f"No {prop} set for the `{name}` Record."
        return str(prop_val)

    # Handle Unset functionality
    if value == "":
        setattr(record, prop, None)
        return f"Unset {prop} of the `{name}` Record."

    # Handle Set functionality
    set_prop_method = getattr(record, "set_" + prop)
    set_prop_method(value)
    return f"Set {prop} to `{value}` for the `{name}` Record."


def render_phones(record: Record) -> str:
    """Render phones table for the specified Record.

    Args:
        record (Record): Record with phones.

    Returns:
        str: Rendered phones table.
    """
    title = f"{record.name} : Phone Numbers"
    tbox = box.SQUARE
    table = Table(title=title, border_style="blue", min_width=50, show_lines=True, box=tbox)
    table.add_column("", style="white", no_wrap=True)
    table.add_column("Phone Number", style="cyan", no_wrap=True)
    for i, phone in enumerate(record.phones):
        table.add_row(str(i), phone.value)

    console = Console(record=True, color_system="standard")
    with console.capture() as capture:
        console.print(table)
    return capture.get()


def render_birthdays(title: str, birthdays: list) -> str:
    """Render birthdays dict.

    Args:
        birthdays (dict): Dictionary with Record birthday info.

    Returns:
        str: Rendered birthdays.
    """
    tbox = box.SQUARE
    table = Table(title=title, border_style="blue", min_width=50, show_lines=True, box=tbox)
    table.add_column("Name", style="white", no_wrap=True)
    table.add_column("Congratulation Date", style="yellow", no_wrap=True)
    table.add_column("Days Left", style="cyan", no_wrap=True)
    table.add_column("Next Birthday Age", style="yellow", no_wrap=True)
    for row in birthdays:
        name = str(row["record"].name)
        congrats_date = str(row["congratulation_date"])
        table.add_row(name, congrats_date, str(row["wait_days_count"]), str(row["next_age"]))

    console = Console(record=True, color_system="standard")
    with console.capture() as capture:
        console.print(table)
    return capture.get()


def render_records(title: str, records: dict, keyword_highlight: str = None) -> str:
    """Render Records table.

    Args:
        record (Record): Record object.

    Returns:
        str: Rendered Record "view".
    """
    tbox = box.SQUARE
    table = Table(title=title, border_style="blue", min_width=50, show_lines=True, box=tbox)
    table.add_column("Name", style="white", no_wrap=True)
    table.add_column("Birthday", style="yellow", no_wrap=True)
    table.add_column("Address", style="cyan")
    table.add_column("Email", style="yellow", no_wrap=True)
    table.add_column("Phone Numbers", style="cyan")
    for record in records.values():
        name_str = str(record.name)
        birthday_str = str(record.birthday) if record.birthday else ""
        address_str = str(record.address) if record.address else ""
        email_str = str(record.email) if record.email else ""
        phones_str = " ; ".join(phone.value for phone in record.phones) if record.phones else ""
        table.add_row(name_str, birthday_str, address_str, email_str, phones_str)

    console = Console(record=True, color_system="standard")
    with console.capture() as capture:
        console.print(table)
    output = capture.get()

    if not keyword_highlight:
        return output

    BG_MAGENTA = "\x1b[45m"  # set background to magenta
    BG_RESET  = "\x1b[49m"  # reset only background (keeps other styles)

    # Highlight all occurrences, except those which start with `
    pattern = re.compile(rf"(?<!`){re.escape(keyword_highlight)}")
    return pattern.sub(lambda m: f"{BG_MAGENTA}{m.group(0)}{BG_RESET}", output)


def render_notes(title: str, notes: dict, keyword_highlight: str = None) -> str:
    """Render Notes table.

    Args:
        notes (dict): dict of Notes.

    Returns:
        str: Rendered Notes table.
    """
    tbox = box.SQUARE
    table = Table(title=title, border_style="blue", min_width=50, show_lines=True, box=tbox)
    table.add_column("ID", style="white", no_wrap=True)
    table.add_column("Body Text", style="cyan", no_wrap=True)
    table.add_column("Tags", style="yellow")
    for note in notes.values():
        id_str = str(note.id)
        body_str = str(note.body) if note.body else ""
        tags_str = " ; ".join(tag.value for tag in note.tags) if note.tags else ""
        table.add_row(id_str, body_str, tags_str)

    console = Console(record=True, color_system="standard")
    with console.capture() as capture:
        console.print(table)
    output = capture.get()

    if not keyword_highlight:
        return output

    BG_MAGENTA = "\x1b[45m"  # set background to magenta
    BG_RESET  = "\x1b[49m"  # reset only background (keeps other styles)

    # Highlight all occurrences, except those which start with `
    pattern = re.compile(rf"(?<!`){re.escape(keyword_highlight)}")
    return pattern.sub(lambda m: f"{BG_MAGENTA}{m.group(0)}{BG_RESET}", output)


@input_error
def handle_birthdays(args: list[str], book: AddressBook) -> str:
    """Handle birthdays command.

    If args is empty:
        Output table of records with upcoming birthdays, which occur
        within default range: 7 days.
    If args has 1 item:
        Output table of records with upcoming birthdays, which occur
        within specified range in days.

    Args:
        args (list[str]): List with raw cmd arguments.
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or upcoming birthdays table.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        InvalidCmdArgTypeError: If input argument has wrong type.
    """
    try:
        days, *_ = args
    except:
        raise InvalidCmdArgsCountError

    # Validate input and apply default if needed
    try:
        days = 7 if days is None else int(days)
    except ValueError as e:
        raise InvalidCmdArgTypeError from e

    birthdays = book.get_upcoming_birthdays(days)
    return render_birthdays(f"Upcoming Birthdays in Next {days} Days", birthdays)


@input_error
def handle_find_records(args: list[str], book: AddressBook) -> str:
    """Handle find-records command.

    Search Records by all supported fields.

    Args:
        args (list[str]): List with raw cmd arguments.
            Expected: [keyword].
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or matched Record "views".

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
    """
    try:
        keyword, *_ = args
    except:
        raise InvalidCmdArgsCountError

    records = book.find(keyword)

    if not records:
        return f"No Record matches for the `{keyword}` keyword."

    # Render all matched Records
    return render_records(f"Records matching `{keyword}`", records, keyword)


@input_error
def handle_new_note(args: list[str], notebook: NoteBook) -> str:
    """Handle new-note command.

    Create new Note.

    Args:
        args (list[str]): List with raw cmd arguments.
            Expected: [body].
        notebook (NoteBook): NoteBook object.

    Returns:
        str: Operation result message.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        InvalidPropertyFormatError: If body format is invalid.
    """
    try:
        body, *_ = args
    except:
        raise InvalidCmdArgsCountError

    note = Note(body)
    notebook.add_note(note)
    return f"New Note with ID #{note.id} was created."


@input_error
def handle_notes(args: list[str], notebook: NoteBook) -> str:
    """Handle note commands: all, show, update, or delete.

    If args is empty:
        Show "views" for all Notes.
    If args has 1 item:
        Show "view" for specified Note.
    If args contains 2 items:
        Update specified Nate with the new value.
        If value is empty string, then delete specified Note.

    Args:
        args (list[str]): List with raw cmd arguments.
            Expected: [] or [id] or [id, body] or [id, ""]
        notebook (NoteBook): NoteBook object.

    Returns:
        str: Operation result message or Note "view".

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        NoteNotExistsError: If specified Note doesn't exist.
        InvalidCmdArgTypeError: If ID is not a valid integer.
        InvalidPropertyFormatError: If new body format is invalid.
    """
    try:
        id_, body, *_ = args
    except:
        raise InvalidCmdArgsCountError

    # Handle ShowAll functionality
    if id_ is None:
        return render_notes("All Notes", notebook) if notebook else "No Notes."

    # Validate `id` argument
    try:
        id_ = int(id_)
        if id_ < 0:
            raise ValueError
    except ValueError:
        raise InvalidCmdArgTypeError("Note ID must be a positive integer.")

    note = notebook.get_note(id_)

    # If Note wasn't found, raise error for all cases except "ShowAll" functionality
    if note is None:
        raise NoteNotExistsError

    # Handle Show functionality
    if body is None:
        return render_notes("", {0: note})

    # Handle Delete functionality
    if body == "":
        notebook.delete_note(id_)
        return f"Deleted Note #`{id_}`."

    # Handle Update functionality
    notebook.update_note(id_, body)
    return f"Updated Note #`{id_}` with new body content."


@input_error
def handle_tag(args: list[str], notebook: NoteBook) -> str:
    """Handle tag command: show, add, replace, delete.

    If args has 1 item:
        Show all tags for the specified Note.
    If args has 2 items:
        Add tag to the specified Note.
    If args has 3 items:
        Replace specified tag with new value in specified Note.
        If new value is empty string, then delete specified tag.

    Args:
        args (list[str]): List with raw cmd arguments.
            Expected: [note_id] or [note_id, value] or
            [note_id, value, replace_value] or [note_id, value, ""].
        notebook (NoteBook): NoteBook object.

    Returns:
        str: Operation result message or tags list.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        NoteNotExistsError: If specified Note doesn't exist.
        TagNotExistsError: If specified Tag doesn't exist.
        InvalidCmdArgTypeError: If ID is not a valid integer.
        InvalidPropertyFormatError: If new body format is invalid.
    """
    try:
        note_id, value, replace_value, *_ = args
    except:
        raise InvalidCmdArgsCountError

    # Validate `id` argument
    try:
        note_id = int(note_id)
        if note_id < 0:
            raise ValueError
    except ValueError:
        raise InvalidCmdArgTypeError("Note ID must be a positive integer.")

    note = notebook.get_note(note_id)

    # If Note wasn't found, raise error
    if note is None:
        raise NoteNotExistsError

    # Handle Get functionality
    if value is None:
        output = "\n".join(tag.value for tag in note.tags)
        return output if output else f"No tags found for the Note #`{note_id}`."

    # Handle Add functionality
    if replace_value is None:
        if note.add_tag(value):
            return f"Added `{value}` tag to the Note #`{note_id}`."
        else:
            return f"Skipped duplicate `{value}` tag in the Note #`{note_id}`."

    # Check if specified tag field exists
    tag = note.find_tag(value)
    if tag is None:
        raise TagNotExistsError

    # Handle Delete functionality
    if replace_value == "":
        note.remove_tag(value)
        return f"Deleted `{value}` tag from the Note #`{note_id}`."

    # Handle Update functionality
    tag.set_value(replace_value)
    return f"Replaced `{value}` tag with `{replace_value}` in the Note #`{note_id}`."


@input_error
def handle_find_notes(args: list[str], notebook: NoteBook) -> str:
    """Handle find-notes command.

    Search Notes by all supported fields.

    Args:
        args (list[str]): List with raw cmd arguments.
            Expected: [keyword].
        notebook (NoteBook): NoteBook object.

    Returns:
        str: Operation result message or matched Note "views".

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
    """
    try:
        keyword, *_ = args
    except:
        raise InvalidCmdArgsCountError

    notes = notebook.find(keyword)

    if not notes:
        return f"No Note matches for the `{keyword}` keyword."

    # Render all matched Notes
    return render_notes(f"Records matching `{keyword}`", notes, keyword)


@input_error
def handle_encryption(args: list[str], config: dict) -> str:
    """Handle encryption command.

    Activate/deactivate encryption for storage file.

    Args:
        args (list[str]): List with raw cmd arguments.
            Expected: [flag].
        notebook (NoteBook): NoteBook object.

    Returns:
        str: Operation result message.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
    """
    try:
        flag, *_ = args
    except:
        raise InvalidCmdArgsCountError

    flag = flag.lower();
    if flag == "on" and config["encryption_key"] is None:
        key = Fernet.generate_key().decode()
    elif flag == "off":
        key = None
    else:
        raise InvalidCmdArgTypeError

    config["encryption_key"] = key
    return f"Encryption status: {flag}."


def load_store(path: str, cfg_path: str) -> dict:
    """Load app data from the encrypted/plain Pickle-serialized file.

    Args:
        path (str): Path to the data file.
        cfg_path (str): Path to the config file.

    Returns:
        dict: Restored objects or empty objects on error.
    """
    cfg = {"encryption_key": None}
    key = None
    recreate_config = False

    # Try to load encryption key from config.json
    try:
        with open(cfg_path, "r", encoding="utf-8") as fh:
            config = json.load(fh)
        key = config.get("encryption_key")
        if key is not None and not (isinstance(key, str) and str):
            raise ValueError
    except FileNotFoundError:
        print(f"INFO: Config `{cfg_path}` wasn't found.")
        recreate_config = True
    except (OSError, json.JSONDecodeError, ValueError):
        print(
            f"ERROR: There was a problem reading `{cfg_path}` config file.\n"
            "        To prevent potential data loss, please fix issues or delete file."
        )
        return None

    cfg["encryption_key"] = key

    if recreate_config:
        try:
            with open(cfg_path, "w", encoding="utf-8") as fh:
                json.dump(cfg, fh, indent=4)
                print(f"INFO: Created empty `{cfg_path}` config file.")
        except OSError as e:
            print(f"ERROR: There was a problem creating `{cfg_path}` config file.")
            return None

    data = {}

    # Open data file for reading
    try:
        with open(path, "rb") as fh:
            # If key is None, then load as unencrypted file
            if key is None:
                data = pickle.load(fh)
            else:
                # Create Fernet object and decrypt
                fernet = Fernet(key.encode())
                encrypted_data = fh.read()
                decrypted_data = fernet.decrypt(encrypted_data)
                data = pickle.loads(decrypted_data)
    except FileNotFoundError:
        print(f"INFO: File `{path}` wasn't found. Starting with empty app data.")
    except OSError:
        print(
            f"ERROR: There was a problem reading `{path}` file. "
            "        To prevent potential data loss, please fix issues."
            "        Or delete file if you want to start with empty app data."
        )
        return None

    data.setdefault("config", cfg)
    data.setdefault("meta", {"NoteBook.id_iter": 1})
    data.setdefault("book", AddressBook())
    data.setdefault("notebook", NoteBook())

    NoteBook.reset_id(data["meta"]["NoteBook.id_iter"] + 1)

    return data


@file_error
def save_store(data: dict, path: str, cfg_path: str) -> str:
    """Save app data to the encrypted/plain Pickle-serialized file.

    Args:
        data (dict): Dict with app data to save.
        path (str): Path to the data file.
        cfg_path (str): Path to the config file.

    Returns:
        str: Operation result message.
    """
    data["meta"]["NoteBook.id_iter"] = NoteBook.last_id

    key = data["config"]["encryption_key"]

    # Save config
    try:
        with open(cfg_path, "w", encoding="utf-8") as fh:
            json.dump(data["config"], fh, indent=4)
    except OSError as e:
        print(f"ERROR: There was a problem saving `{cfg_path}` config file.")
        return None

    try:
        with open(path, "wb") as fh:
            if key is None:
                pickle.dump(data, fh)
            else:
                # Create Fernet and encrypt
                fernet = Fernet(key.encode())
                serialized_data = pickle.dumps(data)
                encrypted_data = fernet.encrypt(serialized_data)
                fh.write(encrypted_data)

    except OSError as e:
        raise OSError(f"ERROR: Failed to save app data in `{path}` file.") from e
    if key is None:
        return f"App data was saved in `{path}` file."
    return f"App data was encrypted and saved in `{path}` file."
