import functools
import pickle
from collections.abc import Callable

from contacts import (
    AddressBook,
    Record,
    InvalidPhoneFormatError,
    InvalidDateFormatError,
    InvalidNameFormatError,
    InvalidAddressFormatError,
    InvalidEmailFormatError,
)


class InvalidCmdArgsCountError(ValueError):
    """Custom exception for invalid cmd args count."""

    def __init__(self, message="Invalid cmd args count."):
        super().__init__(message)


class InvalidCmdArgTypeError(ValueError):
    """Custom exception for invalid cmd argument type."""

    def __init__(self, message="Invalid cmd argument data type."):
        super().__init__(message)


class RecordNotExists(ValueError):
    """Custom exception if specified Record doesn't exist."""

    def __init__(self, message="Specified Record doesn't exist."):
        super().__init__(message)


class FieldNotExists(ValueError):
    """Custom exception if specified Field doesn't exist."""

    def __init__(self, message="Specified Field doesn't exist."):
        super().__init__(message)


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
            InvalidCmdArgsCountError, RecordNotExists, FieldNotExists, InvalidPhoneFormatError,
            InvalidDateFormatError, InvalidNameFormatError, InvalidAddressFormatError,
            InvalidEmailFormatError, InvalidCmdArgTypeError
        ) as e:
            return f"ERROR: {e.args[0]} Try again."
    return inner


@input_error
def handle_record(args: list[str], book: AddressBook) -> str:
    """Handle record commands: create/show, rename, delete.

    If args has 1 item:
        Show specified Record. Create new Record if missing.
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
        RecordNotExists: If specified Record doesn't exist.
        InvalidNameFormatError: If new name format is invalid.
    """
    try:
        name, value, *_ = args
    except:
        raise InvalidCmdArgsCountError

    record = book.find_record(name)
    is_new_record = False

    # If Record wasn't found, raise error for all cases except "Create/Show" functionality
    if record is None:
        if value is not None:
            raise RecordNotExists
        record = Record(name)
        book.add_record(record)
        is_new_record = True

    # Handle Create/Show functionality
    if value is None:
        if is_new_record:
            return f"New `{name}` Record was created."
        return render_record_table(name, book)
    # Handle Delete functionality
    if value == "":
        book.delete_record(name)
        return f"Deleted `{name} Record."
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
        RecordNotExists: If specified Record doesn't exist.
        FieldNotExists: If specified phone doesn't exist.
        InvalidPhoneFormatError: If new phone number format is invalid.
    """
    try:
        name, value, replace_value, *_ = args
    except:
        raise InvalidCmdArgsCountError

    record = book.find_record(name)

    # If Record wasn't found, raise error
    if record is None:
        raise RecordNotExists

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
            raise FieldNotExists
        # Handle Delete functionality
        if replace_value == "":
            record.remove_phone(value)
            return f"Deleted `{value}` phone from the `{name}` Record."
        # Handle Update functionality
        phone.set_value(replace_value)
        return f"Changed `{value}` phone to `{replace_value}` for the `{name}` Record."


@input_error
def handle_address(args: list[str], book: AddressBook) -> str:
    """Handle address commands: show, set, unset.

    If args has 1 item:
        Show address of the specified Record.
    If args has 2 items:
        Set address of the specified Record.
        If new value is empty string, then unset address field.

    Args:
        args (list[str]): List with raw cmd arguments.
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or address value.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExists: If specified Record doesn't exist.
        InvalidAddressFormatError: If address format is invalid.
    """
    try:
        name, value, *_ = args
    except:
        raise InvalidCmdArgsCountError

    record = book.find_record(name)

    # If Record wasn't found, raise error
    if record is None:
        raise RecordNotExists

    # Handle Get functionality
    if value is None:
        if record.address is None:
            return f"No address set for the `{name}` Record."
        return record.address.value
    # Handle Unset functionality
    if value == "":
        record.address = None
        return f"Unset address of the `{name}` Record."
    # Handle Set functionality
    if value is not None:
        record.set_address(value)
        return f"Set address to `{value}` for the `{name}` Record."


@input_error
def handle_email(args: list[str], book: AddressBook) -> str:
    """Handle email commands: show, set, unset.

    If args has 1 item:
        Show email of the specified Record.
    If args has 2 items:
        Set email of the specified Record.
        If new value is empty string, then unset email field.

    Args:
        args (list[str]): List with raw cmd arguments.
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or email value.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExists: If specified Record doesn't exist.
        InvalidEmailFormatError: If email format is invalid.
    """
    try:
        name, value, *_ = args
    except:
        raise InvalidCmdArgsCountError

    record = book.find_record(name)

    # If Record wasn't found, raise error
    if record is None:
        raise RecordNotExists

    # Handle Get functionality
    if value is None:
        if record.email is None:
            return f"No email set for the `{name}` Record."
        return record.email.value
    # Handle Unset functionality
    if value == "":
        record.email = None
        return f"Unset email of the `{name}` Record."
    # Handle Set functionality
    if value is not None:
        record.set_email(value)
        return f"Set email to `{value}` for the `{name}` Record."


@input_error
def handle_birthday(args: list[str], book: AddressBook) -> str:
    """Handle birthday commands: show, set, unset.

    If args has 1 item:
        Show birthday of the specified Record.
    If args has 2 items:
        Set birthday of the specified Record.
        If new value is empty string, then unset birthday field.

    Args:
        args (list[str]): List with raw cmd arguments.
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or birthday textual representation.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExists: If specified Record doesn't exist.
        InvalidDateFormatError: If date format is invalid.
    """
    try:
        name, value, *_ = args
    except:
        raise InvalidCmdArgsCountError

    record = book.find_record(name)

    # If Record wasn't found, raise error
    if record is None:
        raise RecordNotExists

    # Handle Get functionality
    if value is None:
        if record.birthday is None:
            return f"No birthday set for the `{name}` Record."
        return str(record.birthday)
    # Handle Unset functionality
    if value == "":
        record.birthday = None
        return f"Unset birthday of the `{name}` Record."
    # Handle Set functionality
    if value is not None:
        record.set_birthday(value)
        return f"Set birthday to `{value}` for the `{name}` Record."


@input_error
def render_record_table(args: dict[str, str], book: AddressBook) -> str:
    """Render Record fields table.

    Render single Record if name is provided. Otherwise render all.

    Args:
        args (dict[str, str]): Dict with raw cmd arguments.
            Keys: name (optional).
        book (AddressBook): AddressBook object.

    Returns:
        str: Rendered Record fields table.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExists: If specified Record doesn't exist.
    """
    try:
        name, *_ = args
    except:
        print(args)
        print("zzz")
        raise InvalidCmdArgsCountError

    src = book

    # Render single Record if name was specified
    if name:
        record = book.find_record(name)
        # Check if specified Record exists
        if record is None:
            raise RecordNotExists
        src = AddressBook()
        src.add_record(record)

    # Build output
    output = ""
    for name, record in src.items():
        output += "/" + '═' * 30 + "\\\n"
        output += "│" + f" Name: {name}".ljust(30) + "│\n"
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
    except FileNotFoundError:
        print(f"INFO: File `{path}` wasn't found. Starting with an empty AdressBook.")
    except OSError:
        print(
            f"ERROR: There was a problem reading `{path}` file. "
            "Starting with an empty AddressBook.\n"
            "Be careful, since your existing AddressBook may be overwritten."
        )
    return AddressBook()


def save_data(book: AddressBook, path: str):
    """Save AddressBook object to the Pickle-serialized data file.

    Args:
        book (AddressBook): Source object.
        path (str): Path to the data file.
    """
    try:
        with open(path, "wb") as fh:
            pickle.dump(book, fh)
    except OSError:
        print(f"ERROR: Failed to save AddressBook in `{path}` file.")
    else:
        print(f"AddressBook was saved in `{path}` file.")
