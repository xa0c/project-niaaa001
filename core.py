import ascii_magic
import functools
import pickle
from collections.abc import Callable

from contacts import AddressBook, Record
from contacts import InvalidPropertyFormatError


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


class FieldNotExistsError(ValueError):
    """Custom exception if specified Field doesn't exist."""

    def __init__(self, message="Specified Field doesn't exist."):
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
            InvalidCmdArgsCountError, RecordExistsError, RecordNotExistsError, FieldNotExistsError,
            InvalidPropertyFormatError, InvalidCmdArgTypeError
        ) as e:
            return f"ERROR: {e.args[0]} Try again."
    return inner


@input_error
def handle_new_record(args: list[str], book: AddressBook) -> str:
    """Handle new record command.

    Create new Record.

    Args:
        args (list[str]): List with raw cmd arguments.
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        InvalidPropertyFormatError: If name format is invalid.
    """
    try:
        name, value, *_ = args
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
    """Handle record commands: show, rename, delete.

    If args is empty:
        Show "cards" for all Records.
    If args has 1 item:
        Show "card" for specified Record.
    If args contains 2 items:
        Rename specified Record with the new value.
        If value is empty string, then delete specified Record.

    Args:
        args (list[str]): List with raw cmd arguments.
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or Record "card".

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
        output = ""
        for record in book.values():
            output += render_record_table(record)
        return output if output else "No Records."

    record = book.get_record(name)

    # If Record wasn't found, raise error for all cases except "ShowAll" functionality
    if record is None:
        raise RecordNotExistsError

    # Handle Show functionality
    if value is None:
        return render_record_table(record)
    # Handle Delete functionality
    if value == "":
        book.delete_record(name)
        return f"Deleted `{name}` Record."
    # Handle Rename functionality
    if value is not None:
        book.rename_record(name, value)
        return f"Renamed `{name}` Record to `{value}`."


@input_error
def handle_phone(args: list[str], book: AddressBook) -> str:
    """Handle phone commands: show, add, edit, delete.

    If args has 1 item:
        Show all phones for the specified Record.
    If args has 2 items:
        Add phone to the specified Record.
    If args has 3 items:
        Replace specified phone with new value in specified Record.
        If new value is empty string, then delete specified phone.

    Args:
        args (list[str]): List with raw cmd arguments.
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or phone numbers.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExistsError: If specified Record doesn't exist.
        FieldNotExistsError: If specified phone doesn't exist.
        InvalidPropertyFormatError: If new phone number format is invalid.
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
    if value is None and replace_value is None:
        output = "\n".join(phone.value for phone in record.phones)
        return output if output else f"No phones found for the `{name}` Record."
    # Handle Add functionality
    if value is not None and replace_value is None:
        record.add_phone(value)
        return f"Added `{value}` phone to the `{name}` Record."
    # Handle Edit/Delete functionality
    if value is not None and replace_value is not None:
        # Check if specified phone field exists
        phone = record.find_phone(value)
        if phone is None:
            raise FieldNotExistsError
        # Handle Delete functionality
        if replace_value == "":
            record.remove_phone(value)
            return f"Deleted `{value}` phone from the `{name}` Record."
        # Handle Update functionality
        phone.set_value(replace_value)
        return f"Changed `{value}` phone to `{replace_value}` for the `{name}` Record."


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
        str: Operation result message or property textual representation.

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
    if value is not None:
        set_prop_method = getattr(record, "set_" + prop)
        set_prop_method(value)
        return f"Set {prop} to `{value}` for the `{name}` Record."


def render_record_table(record: Record) -> str:
    """Render Record fields table.

    Render specified Record "card".

    Args:
        record (Record): Record object.

    Returns:
        str: Rendered Record "card".
    """
    output = "/" + '═' * 30 + "\\\n"
    output += "│" + f" Name: {record.name}".ljust(30) + "│\n"
    if record.birthday is not None:
        output += "│" + f" Birthday: {record.birthday}".ljust(30) + "│\n"
    if record.address is not None:
        output += "│" + f" Address: {record.address}".ljust(30) + "│\n"
    if record.email is not None:
        output += "│" + f" Email: {record.email}".ljust(30) + "│\n"
    output += "├" + "─" * 30 + "┤\n"
    output += "│" + "Phones".center(30) + "│\n"
    output += "│" + "-" * 30 + "│\n"

    for phone in record.phones:
        output += "│ " + str(phone).ljust(29) + "│\n"
    output += "└" + "─" * 30 + "┘\n"
    return output


@input_error
def handle_birthdays(args: list[str], book: AddressBook) -> str:
    """Handle birthdays command.

    If args is empty:
        Output table of records with upcoming birthdays, which occur \
        within default range: 7 days.
    If args has 1 item:
        Output table of records with upcoming birthdays, which occur \
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

    result = book.get_upcoming_birthdays(days)

    # Assemble table
    output_list = []
    for row in result:
        s = str(row["congratulation_date"])
        s += f" (in {row["wait_days_count"]} "
        s += "day): " if row["wait_days_count"] == 1 else "days): "
        s += str(row["record"].name)
        output_list.append(s)

    return "\n".join(output_list)


@input_error
def handle_find_records(args: list[str], book: AddressBook) -> str:
    """Handle find command.

    Search Records by all supported fields.

    Args:
        args (list[str]): List with raw cmd arguments.
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or matched Record "cards".

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
    """
    try:
        search_value, *_ = args
    except:
        raise InvalidCmdArgsCountError

    records = book.find(search_value)

    if not records:
        return f"No Record matches for the `{search_value}` keyword."

    # Render all matched Record "cards"
    output = ""
    for record in records:
        output += render_record_table(record)
    return output


@file_error
def load_data(path: str) -> AddressBook:
    """Load AddressBook object from the Pickle-serialized data file.

    Args:
        path (str): Path to the data file.

    Returns:
        AddressBook: Restored object or empty on file access error.
    """
    try:
        with open(path, "rb") as fh:
            return pickle.load(fh)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"INFO: File `{path}` wasn't found. Starting with an empty AdressBook."
        ) from e
    except OSError as e:
        raise OSError(
            f"ERROR: There was a problem reading `{path}` file. "
            "Starting with an empty AddressBook.\n"
            "Be careful, since your existing AddressBook may be overwritten."
        ) from e
    return AddressBook()


@file_error
def save_data(book: AddressBook, path: str) -> str:
    """Save AddressBook object to the Pickle-serialized data file.

    Args:
        book (AddressBook): Source object.
        path (str): Path to the data file.

    Returns:
        str: Operation result message.
    """
    try:
        with open(path, "wb") as fh:
            pickle.dump(book, fh)
    except OSError as e:
        raise OSError(f"ERROR: Failed to save AddressBook in `{path}` file.") from e
    return f"AddressBook was saved in `{path}` file."
