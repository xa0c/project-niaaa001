import io
import re
from collections import UserDict
from datetime import date, datetime

from PIL import Image
from ascii_magic import AsciiArt

import utils


BIRTHDAY_FORMAT = "%d.%m.%Y"
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


class InvalidPropertyFormatError(ValueError):
    """Custom exception for invalid property format."""

    def __init__(self, message="Invalid property format."):
        super().__init__(message)


class InvalidPhoneFormatError(InvalidPropertyFormatError):
    """Custom exception for invalid phone format."""

    def __init__(self, message="Invalid phone format: must be 10 ASCII digits starting with 0."):
        super().__init__(message)


class InvalidDateFormatError(InvalidPropertyFormatError):
    """Custom exception for invalid date format."""

    def __init__(self, message="Invalid date format: must be `DD.MM.YYYY`."):
        super().__init__(message)


class InvalidNameFormatError(InvalidPropertyFormatError):
    def __init__(self, message="Invalid name format: length must be <= 20."):
        super().__init__(message)


class InvalidAddressFormatError(InvalidPropertyFormatError):
    def __init__(self, message="Invalid address format: length must be <= 300."):
        super().__init__(message)


class InvalidEmailFormatError(InvalidPropertyFormatError):
    def __init__(self, message="Invalid email format: must match pattern and length <= 254."):
        super().__init__(message)


class FileAccessError(InvalidPropertyFormatError):
    def __init__(self, message="Resource path can't be read at this moment."):
        super().__init__(message)


class InvalidPhotoFormatError(InvalidPropertyFormatError):
    def __init__(self, message="Invalid photo format."):
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


class Photo(Field):
    """Field class for storing Record photo filepath field."""

    def __init__(self, value: str):
        self.set_value(value)

    def __str__(self):
        return self.render()

    def set_value(self, value: str):
        """Setter with input validation.

        Get image from Web/FS, thumbnail to 256x256 JPEG, save as bytes.

        Raises:
            FileNotFoundError: If filepath wasn't found.
            FileAccessError: If filepath can't be accessed.
            InvalidPhotoFormatError: If file can't be processed.
        """
        # Load image resource from specified location
        try:
            if value.startswith("http://") or value.startswith("https://"):
                art = AsciiArt.from_url(value)
            else:
                art = AsciiArt.from_image(value)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File `{value}` wasn't found") from e
        except OSError as e:
            raise FileAccessError from e

        # Generate byte string from provided image
        try:
            art.image.thumbnail((256, 256), resample=Image.LANCZOS)
            img_byte_arr = io.BytesIO()
            img = art.image
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.save(img_byte_arr, format="JPEG")
        except e:
            raise InvalidPhotoFormatError from e
        self.value = img_byte_arr.getvalue()

    def render(self, columns: int = 120, width_ratio: float = 2.125):
        """Return bg/fg-colored string representation of photo.

        Args:
            columns (int): Width of the output in charactres.
            width_ration (float): Terminal-specific character ratio.
        """
        art = AsciiArt(Image.open(io.BytesIO(self.value)))
        return utils.get_truecolor_string(art, columns=columns, width_ratio=width_ratio)


class Record:
    """Record for contact info management.

    Attributes:
        name (Field)
        phones (list[Phone])
        birthday (Field)
        address (Field)
        email (Field)
        photo (Field)

    Args:
        name: Name field value.
    """

    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.address = None
        self.email = None
        self.photo = None

    def __str__(self):
        return f"Contact name: {self.name}, phones: {'; '.join(p.value for p in self.phones)}"

    def add_phone(self, value: str) -> bool:
        """Add phone to the list avoiding the duplicates.

        Args:
            value (str): String value of the phone to add.

        Raises:
            InvalidPhoneFormatError: If phone format is invalid.

        Returns:
            bool: True if phone was added. False if skipped duplicate.
        """
        if value in self.phones:
            return False

        self.phones.append(Phone(value))
        return True

    def remove_phone(self, value: str):
        """Remove phone from the list.

        Args:
            value (str): String value of the phone to remove.

        Raises:
            ValueError: If phone not found.
        """
        self.phones.remove(value)

    def edit_phone(self, old_value: str, new_value: str):
        """Replace existing phone with new value.

        Args:
            old_value (str): String value of the existing phone.
            new_value (str): String value of the new phone.

        Raises:
            ValueError: If value lookup fails.
            IndexError: If item disappears before referencing.
            InvalidPhoneFormatError: If phone format is invalid.
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

    def set_photo(self, value: str):
        """Set photo for the record.

        Args:
            value (str): String value of the photo filepath or URL to set.
        """
        self.photo = Photo(value)


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

    def get_record(self, name: str = None) -> Record | None:
        """Return Record by name.

        Args:
            name (str): Key of the Record to get.

        Returns:
            Record or None: Object if found. None otherwise.
        """
        return self.data.get(name)

    def find(self, search_value: str = None) -> list[Record]:
        """Find all Records matching search value.

        Searchable fields: name, birthday, phones, email, address.

        Args:
            search_value (str): Matching value to find.

        Returns:
            list[Record]: List of matched Records.
        """
        records = []
        search_value = search_value.lower()
        for record in self.values():
            if (
                search_value in record.name.value.lower() or
                (record.birthday and search_value in str(record.birthday)) or
                (record.address and search_value in record.address.value.lower()) or
                (record.email and search_value in record.email.value.lower()) or
                any(search_value in phone.value for phone in record.phones)
            ):
                records.append(record)
        return records

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
        this_is_leap_year = utils.is_leap_year(today.year)
        next_is_leap_year = utils.is_leap_year(today.year + 1)

        for rec in self.data.values():
            # Process only records with non-None birthdays
            if rec.birthday is None:
                continue

            bd = rec.birthday.value
            next_age = today.year - bd.year
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
                next_age += 1

            # Count remaining days
            wait_days_count = (congrats_date - today).days

            # Include only those within next `days`
            if 0 <= wait_days_count <= days:
                result.append({
                    "record": rec,
                    "congratulation_date": congrats_date,
                    "wait_days_count": wait_days_count,
                    "next_age": next_age,
                })

        # Sort results by congratulation_date
        return sorted(result, key=lambda d: d["congratulation_date"])
