import functools
import pickle
from collections.abc import Callable
from contacts import (
    AddressBook, Record, InvalidPhoneFormatError, InvalidDateFormatError,
    InvalidNameFormatError, InvalidAddressFormatError, InvalidEmailFormatError,
    Address, Email, Birthday
)


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
            InvalidDateFormatError, InvalidNameFormatError, InvalidAddressFormatError,
            InvalidEmailFormatError
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
def phone_command(args: dict[str, str], book: AddressBook) -> str:
    """Handle phone command: show, add, edit, or delete phones.

    Args:
        args (dict[str, str]): Dict with raw cmd arguments.
            Keys: name, value (optional for add), old_value (optional for change/delete),
            new_value (optional for change/delete).
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or phone numbers.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExists: If specified Record doesn't exist.
        FieldNotExists: If specified phone field doesn't exist.
        InvalidPhoneFormatError: If phone number has invalid format.
    """
    try:
        name = args.get("name")
        value = args.get("value")
        old_value = args.get("old_value")
        new_value = args.get("new_value")
    except:
        raise InvalidCmdArgsCountError

    if name is None:
        raise InvalidCmdArgsCountError

    record = book.find(name)

    if value is None and old_value is None:
        if record is None:
            raise RecordNotExists
        phones = "\n".join(phone.value for phone in record.phones)
        return phones if phones else "No phones found."

    if value is not None and old_value is None:
        if record is None:
            record = Record(name)
            record.add_phone(value)
            book.add_record(record)
            return f"Added '{value}' phone to the new Record."
        else:
            record.add_phone(value)
            return f"Added '{value}' phone to the Record."

    if old_value is not None and new_value == "":
        if record is None:
            raise RecordNotExists
        phone = record.find_phone(old_value)
        if phone is None:
            raise FieldNotExists
        record.remove_phone(old_value)
        return f"Deleted phone '{old_value}' from the Record."

    if old_value is not None and new_value is not None and new_value != "":
        if record is None:
            raise RecordNotExists
        phone = record.find_phone(old_value)
        if phone is None:
            raise FieldNotExists
        phone.set_value(new_value)
        return f"Changed phone from '{old_value}' to '{new_value}'."

    raise InvalidCmdArgsCountError


@input_error
def address_command(args: dict[str, str], book: AddressBook) -> str:
    """Handle address command: show, set, or unset address.

    Args:
        args (dict[str, str]): Dict with raw cmd arguments.
            Keys: name, value (optional).
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or address value.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExists: If specified Record doesn't exist.
        InvalidAddressFormatError: If address format is invalid.
    """
    try:
        name = args.get("name")
        value = args.get("value")
    except:
        raise InvalidCmdArgsCountError

    if name is None:
        raise InvalidCmdArgsCountError

    record = book.find(name)

    if record is None:
        raise RecordNotExists

    if value is None:
        address = getattr(record, 'address', None)
        if address is None:
            return "No address set."
        return address.value

    if value == "":
        record.address = None
        return "Unset address."

    record.address = Address(value)
    return f"Set address to '{value}'."


@input_error
def email_command(args: dict[str, str], book: AddressBook) -> str:
    """Handle email command: show, set, or unset email.

    Args:
        args (dict[str, str]): Dict with raw cmd arguments.
            Keys: name, value (optional).
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or email value.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExists: If specified Record doesn't exist.
        InvalidEmailFormatError: If email format is invalid.
    """
    try:
        name = args.get("name")
        value = args.get("value")
    except:
        raise InvalidCmdArgsCountError

    if name is None:
        raise InvalidCmdArgsCountError

    record = book.find(name)

    if record is None:
        raise RecordNotExists

    if value is None:
        email = getattr(record, 'email', None)
        if email is None:
            return "No email set."
        return email.value

    if value == "":
        record.email = None
        return "Unset email."

    record.email = Email(value)
    return f"Set email to '{value}'."


@input_error
def birthday_command(args: dict[str, str], book: AddressBook) -> str:
    """Handle birthday command: show, set, or unset birthday.

    Args:
        args (dict[str, str]): Dict with raw cmd arguments.
            Keys: name, value (optional).
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or birthday value.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExists: If specified Record doesn't exist.
        InvalidDateFormatError: If birthday format is invalid.
    """
    try:
        name = args.get("name")
        value = args.get("value")
    except:
        raise InvalidCmdArgsCountError

    if name is None:
        raise InvalidCmdArgsCountError

    record = book.find(name)

    if record is None:
        raise RecordNotExists

    if value is None:
        birthday = getattr(record, 'birthday', None)
        if birthday is None:
            return "No birthday set."
        return str(birthday)

    if value == "":
        record.birthday = None
        return "Unset birthday."

    record.birthday = Birthday(value)
    return f"Set birthday to '{value}'."


@input_error
def name_command(args: dict[str, str], book: AddressBook) -> str:
    """Handle name command: show card, rename record, or delete record.

    Args:
        args (dict[str, str]): Dict with raw cmd arguments.
            Keys: name, value (optional).
        book (AddressBook): AddressBook object.

    Returns:
        str: Operation result message or Record card.

    Raises:
        InvalidCmdArgsCountError: If command has invalid argument count.
        RecordNotExists: If specified Record doesn't exist.
        InvalidNameFormatError: If new name format is invalid.
    """
    try:
        name = args.get("name")
        value = args.get("value")
    except:
        raise InvalidCmdArgsCountError

    if name is None:
        raise InvalidCmdArgsCountError

    record = book.find(name)

    if value is None:
        if record is None:
            raise RecordNotExists
        src = AddressBook()
        src.add_record(record)
        output = ""
        for rec_name, rec in src.items():
            output += "/" + '═' * 30 + "\\\n"
            output += "│" + f" Name: {rec_name}".ljust(30) + "│\n"
            if rec.birthday is not None:
                output += "│" + f" Birthday: {rec.birthday}".ljust(30) + "│\n"
            output += "├" + "─" * 30 + "┤\n"
            output += "│" + "Phones".center(30) + "│\n"
            output += "│" + "-" * 30 + "│\n"
            for phone in rec.phones:
                output += "│ " + str(phone).ljust(29) + "│\n"
            output += "└" + "─" * 30 + "┘\n"
        return output

    if value == "":
        if record is None:
            raise RecordNotExists
        book.delete(name)
        return f"Deleted Record '{name}'."

    if record is None:
        raise RecordNotExists

    if book.find(value) is not None:
        return f"ERROR: Record with name '{value}' already exists. Try again."

    old_name = name
    record.name.set_value(value)
    del book.data[old_name]
    book.data[value] = record
    return f"Renamed Record from '{old_name}' to '{value}'."


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
