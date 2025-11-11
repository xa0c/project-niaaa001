import functools
import pickle
from collections.abc import Callable
from contacts import AddressBook, Record, InvalidPhoneFormatError, InvalidDateFormatError


class InvalidCmdArgsCountError(ValueError):
    """Custom exception for invalid cmd args count."""

    def __init__(self, message="Invalid cmd args count."):
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
            InvalidDateFormatError
        ) as e:
            return f"ERROR: {e.args[0]} Try again."
    return inner


@input_error
def add_contact(args: dict[str, str], book: AddressBook) -> str:
    """Add phone field in the specified Record.

    Create new Record if missing.

    Args:
        args (dict[str, str]): Dict with raw cmd arguments.
            Keys: name, value.
        book (AddressBook): AddressBook object.

    Returns:
        string: Operation result message.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        contacts.InvalidPhoneFormatError: If phone number has invalid
            format.
    """
    try:
        name, value = args.values()
    except:
        raise InvalidCmdArgsCountError

    record = book.find(name)

    # Create new Record if wasn't found and add phone field to it
    if record is None:
        record = Record(name)
        record.add_phone(value)
        book.add_record(record)
        return f"Added '{value}' phone field to the new Record."

    # Update existing record with new phone field
    record.add_phone(value)
    return f"Added '{value}' phone field to the existing Record."


@input_error
def change_contact(args: dict[str, str], book: AddressBook) -> str:
    """Replace specified phone field with new value in specified Record.

    Args:
        args (dict[str, str]): Dict with raw cmd arguments.
            Keys: name, old_value, new_value.
        book (AddressBook): AddressBook object.

    Returns:
        string: Operation result message.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExists: If specified Record doesn't exist.
        FieldNotExists: If specified phone field doesn't exist.
        contacts.InvalidPhoneFormatError: If phone number has invalid
            format.
    """
    try:
        name, old_value, new_value = args.values()
    except:
        raise InvalidCmdArgsCountError

    record = book.find(name)

    # Check if specified Record exists
    if record is None:
        raise RecordNotExists

    # Check if specified phone field exists
    phone = record.find_phone(old_value)
    if phone is None:
        raise FieldNotExists

    phone.set_value(new_value)
    return "Changed phone field."


@input_error
def show_phone(args: dict[str, str], book: AddressBook) -> str:
    """Return all phone fields for the specified Record.

    Args:
        args (dict[str, str]): Dict with raw cmd arguments.
            Keys: name.
        book (AddressBook): AddressBook object.

    Returns:
        str: Multiline string with phone numbers.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExists: If specified Record doesn't exist.
    """
    try:
        name, = args.values()
    except:
        raise InvalidCmdArgsCountError

    record = book.find(name)

    # Check if specified Record exists
    if record is None:
        raise RecordNotExists

    return "\n".join(phone.value for phone in record.phones)


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
        name, = args.values()
    except:
        raise InvalidCmdArgsCountError

    src = book

    # Render single Record if name was specified
    if name:
        record = book.find(name)
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
        output += "├" + "─" * 30 + "┤\n"
        output += "│" + "Phones".center(30) + "│\n"
        output += "│" + "-" * 30 + "│\n"

        for phone in record.phones:
            output += "│ " + str(phone).ljust(29) + "│\n"
        output += "└" + "─" * 30 + "┘\n"
    return output


@input_error
def add_birthday(args: dict[str, str], book: AddressBook) -> str:
    """Add birthday field in the specified Record.

    Create new Record if missing.

    Args:
        args (dict[str, str]): Dict with raw cmd arguments.
            Keys: name, value.
        book (AddressBook): AddressBook object.

    Returns:
        string: Operation result message.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        contacts.InvalidDateFormatError: If date has invalid format.
    """
    try:
        name, value = args.values()
    except:
        raise InvalidCmdArgsCountError

    record = book.find(name)

    # Create new Record if wasn't found and add birthday field to it
    if record is None:
        record = Record(name)
        record.add_birthday(value)
        book.add_record(record)
        return f"Added '{value}' birthday field to the new Record."

    # Update existing record with new birthday field
    record.add_birthday(value)
    return f"Added '{value}' birthday field to the existing Record."


@input_error
def show_birthday(args: dict[str, str], book: AddressBook) -> str:
    """Return birthday field for the specified Record.

    Args:
        args (dict[str, str]): Dict with raw cmd arguments.
            Keys: name.
        book (AddressBook): AddressBook object.

    Returns:
        str: Birthday textual representation.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExists: If specified Record doesn't exist.
    """
    try:
        name, = args.values()
    except:
        raise InvalidCmdArgsCountError

    record = book.find(name)

    # Check if specified Record exists
    if record is None:
        raise RecordNotExists

    return record.birthday


@input_error
def birthdays(args: dict[str, str], book: AddressBook) -> str:
    """Return list of dictionaries with Record name and congrats date.

    Args:
        book (AddressBook): AddressBook object.

    Returns:
        str: Multiline string with Record names and congrat dates.
    """
    result = book.get_upcoming_birthdays(7)

    return "\n".join(row["congratulation_date"] + ": " + row["name"] for row in result)


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
