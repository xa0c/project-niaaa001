import re
from collections import UserDict
from datetime import date, datetime

BIRTHDAY_FORMAT = "%d.%m.%Y"
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def is_leap_year(year: int) -> bool:
    """Check if provided year is a leap year.

    Args:
        year (int): Year to check.

    Returns:
        bool: True if a leap year. False otherwise.
    """
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0


class InvalidPhoneFormatError(ValueError):
    """Custom exception for invalid phone format."""

    def __init__(self, message="Invalid phone format: must be 10 ASCII digits starting with 0."):
        super().__init__(message)


class InvalidDateFormatError(ValueError):
    """Custom exception for invalid date format."""

    def __init__(self, message="Invalid date format: must be `DD.MM.YYYY`."):
        super().__init__(message)


class InvalidNameFormatError(ValueError):
    def __init__(self, message="Invalid name format: length must be <= 20."):
        super().__init__(message)


class InvalidAddressFormatError(ValueError):
    def __init__(self, message="Invalid address format: length must be <= 300."):
        super().__init__(message)


class InvalidEmailFormatError(ValueError):
    def __init__(self, message="Invalid email format: must match pattern and length <= 254."):
        super().__init__(message)


class Field:
    """Base class for storing Record fields.

    Args:
        value: Stored value of arbitary type.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Field class for storing Record name field."""

    def __init__(self, value: str):
        self.set_value(value)

    def set_value(self, value: str):
        if len(value) > 20:
            raise InvalidNameFormatError
        self.value = value


class Phone(Field):
    """Field class for storing Record phone field.

    Equality:
        Allows list.index search by str and Phone.
    """

    def __init__(self, value: str):
        """Same parameters as `Field.__init__`.

        Raises:
            InvalidPhoneFormatError: If phone format is invalid.
        """
        self.set_value(value)

    def __eq__(self, other):
        """See class docstring: Equality."""
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, Phone):
            return self.value == other.value
        return NotImplemented

    def set_value(self, value: str):
        """Setter with input format validation.

        Raises:
            InvalidPhoneFormatError: If phone format is invalid.
        """
        if len(value) != 10 or value[0] != '0' or not (value.isascii() and value.isdigit()):
            raise InvalidPhoneFormatError
        self.value = value


class Birthday(Field):
    """Field class for storing Record birthday field."""

    def __init__(self, value: str):
        """Same parameters as `Field.__init__`.

        Raises:
            InvalidDateFormatError: If date format is invalid.
        """
        self.set_value(value)

    def __str__(self):
        return self.value.strftime(BIRTHDAY_FORMAT)

    def set_value(self, value: str):
        """Setter with input format validation.

        Raises:
            InvalidDateFormatError: If date format is invalid.
        """
        try:
            self.value = datetime.strptime(value, BIRTHDAY_FORMAT).date()
        except ValueError as e:
            raise InvalidDateFormatError from e


class Address(Field):
    """Field class for storing Record address field."""

    def __init__(self, value: str):
        """Same parameters as `Field.__init__`.

        Raises:
            InvalidAddressFormatError: If address format is invalid.
        """
        self.set_value(value)

    def set_value(self, value: str):
        """Setter with input format validation.

        Raises:
            InvalidAddressFormatError: If address format is invalid.
        """
        if len(value) > 300:
            raise InvalidAddressFormatError
        self.value = value


class Email(Field):
    """Field class for storing Record email field."""

    def __init__(self, value: str):
        """Same parameters as `Field.__init__`.

        Raises:
            InvalidEmailFormatError: If email format is invalid.
        """
        self.set_value(value)

    def set_value(self, value: str):
        """Setter with input format validation.

        Raises:
            InvalidEmailFormatError: If email format is invalid.
        """
        if len(value) > 254 or not EMAIL_PATTERN.match(value):
            raise InvalidEmailFormatError
        self.value = value


class Record:
    """Record for contact info management.

    Args:
        name: Name field value.
    """

    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.address = None
        self.email = None

    def __str__(self):
        return f"Contact name: {self.name}, phones: {'; '.join(p.value for p in self.phones)}"

    def add_phone(self, value: str):
        """Add phone to the list.

        Args:
            value (str): String value of the phone to add.

        Raises:
            InvalidPhoneFormatError: If phone format is invalid.
        """
        self.phones.append(Phone(value))

    def remove_phone(self, value: str):
        """Remove phone from the list.

        Args:
            value (str): String value of the phone to remove.

        Raises:
            ValueError: If value lookup fails.
            IndexError: If item disappears before referencing.
        """
        del self.phones[self.phones.index(value)]

    def edit_phone(self, old_value: str, new_value: str):
        """Replace existing phone with new value.

        Args:
            old_value (str): String value of the existing phone.
            new_value (str): String value of the new phone.

        Raises:
            ValueError: If value lookup fails.
            IndexError: If item disappears before referencing.
        """
        self.phones[self.phones.index(old_value)] = Phone(new_value)

    def find_phone(self, value: str) -> Phone | None:
        """Return phone record by string.

        Args:
            value (str): String value of the phone to find.

        Returns:
            Phone or None: Object if found. None otherwise.
        """
        try:
            return self.phones[self.phones.index(value)]
        except (ValueError, IndexError):
            return None

    def set_birthday(self, value: str):
        """Set birthday for the record.

        Args:
            value (str): String value of the birthday to set.

        Raises:
            InvalidDateFormatError: If birthday format is invalid.
        """
        self.birthday = Birthday(value)

    def set_address(self, value: str):
        """Set address for the record.

        Args:
            value (str): String value of the address to set.

        Raises:
            InvalidAddressFormatError: If address format is invalid.
        """
        self.address = Address(value)

    def set_email(self, value: str):
        """Set email for the record.

        Args:
            value (str): String value of the email to set.

        Raises:
            InvalidEmailFormatError: If email format is invalid.
        """
        self.email = Email(value)


class AddressBook(UserDict):
    """AddressBook dict for contact records storage and managemnet."""

    def add_record(self, record: Record):
        """Add new Record to the dict.

        Args:
            record (Record): New Record object to add.
        """
        self.data[record.name.value] = record

    def delete_record(self, name: str):
        """Delete Record from the dict.

        Args:
            name (str): Key of the Record to delete.

        Raises:
            KeyError: If key not found during referencing.
        """
        del self.data[name]

    def rename_record(self, name: str, new_name: str):
        """Rename Record and update name field.

        Args:
            name (str): Existing key of the Record to rename.
            new_name (str): New name.

        Raises:
            KeyError: If key not found during referencing.
        """
        self.data[name].name.set_value(new_name)
        # Preserve position during dict key change
        self.data = {new_name if key == name else key: val for key, val in self.data.items()}

    def find_record(self, name: str, phone: str = None) -> Record | None:
        """Return Record record by name.

        Args:
            name (str): Key of the Record to find.
            phone (str): Optional match by phone string value.

        Returns:
            Record or None: Object if found. None otherwise.
        """
        record = self.data.get(name)
        if record is None:
            return None
        if phone and record.find_phone(phone) is None:
            return None
        return record

    def get_upcoming_birthdays(self, days: int) -> list[dict]:
        """Return upcoming birthdays list.

        Args:
            days (int): Amount of days in future to check birthdays.

        Returns:
            list[dict]: Upcoming birthdays list with dict structure:
                {
                    "record": Record,
                    "congratulation_date": date,
                    "wait_days_count": int,
                }
        """
        result = []
        today = date.today()
        this_is_leap_year = is_leap_year(today.year)
        next_is_leap_year = is_leap_year(today.year + 1)

        for rec in self.data.values():
            # Process only records with non-None birthdays
            if rec.birthday is None:
                continue

            bd = rec.birthday.value
            is_feb29 = bd.month == 2 and bd.day == 29

            # Determine congratulation date in this year
            if is_feb29 and not this_is_leap_year:
                congrats_date = bd.replace(year=today.year, month=3, day=1)
            else:
                congrats_date = bd.replace(year=today.year)

            # If birthday this year already passed, use next year
            if congrats_date < today:
                if is_feb29 and not next_is_leap_year:
                    congrats_date = bd.replace(year=today.year + 1, month=3, day=1)
                else:
                    congrats_date = bd.replace(year=today.year + 1)

            # Count remaining days
            wait_days_count = (congrats_date - today).days

            # Include only those within next `days`
            if 0 <= wait_days_count <= days:
                result.append({
                    "record": rec,
                    "congratulation_date": congrats_date,
                    "wait_days_count": wait_days_count,
                })

        # Sort results by congratulation_date
        return sorted(result, key=lambda d: d["congratulation_date"])
