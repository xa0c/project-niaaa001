import itertools
import re
from collections import UserDict


TAG_PATTERN = re.compile(r'^[a-zA-Z0-9 @#$%&._+-]{3,30}$')


class InvalidPropertyFormatError(ValueError):
    """Custom exception for invalid property format."""

    def __init__(self, message="Invalid property format."):
        super().__init__(message)


class InvalidBodyFormatError(InvalidPropertyFormatError):
    def __init__(self, message="Invalid body format: length must be <= 300."):
        super().__init__(message)


class InvalidTagFormatError(InvalidPropertyFormatError):
    def __init__(self, message="Invalid tag format: must be alphanumeric string with length \
            between 3 30. Other allowed symbols: @ # $ % & . _ + - and space."):
        super().__init__(message)


class Field:
    """Base class for storing Note fields.

    Args:
        value: Stored value of arbitary type.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Body(Field):
    """Field class for storing Note body field."""

    def __init__(self, value: str):
        self.set_value(value)

    def set_value(self, value: str):
        if len(value) > 300:
            raise InvalidBodyFormatError
        self.value = value


class Tag(Field):
    """Field class for storing Note tag field.

    Equality:
        Allows list.index search by str and Tag.
    """

    def __init__(self, value: str):
        """Same parameters as `Field.__init__`.

        Raises:
            InvalidTagFormatError: If tag format is invalid.
        """
        self.set_value(value)

    def __eq__(self, other):
        """See class docstring: Equality."""
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, Tag):
            return self.value == other.value
        return NotImplemented

    def set_value(self, value: str):
        """Setter with input format validation.

        Raises:
            InvalidTagFormatError: If tag format is invalid.
        """
        value = value.strip()
        if not (3 <= len(value) <= 30) or not TAG_PATTERN.match(value):
            raise InvalidTagFormatError
        self.value = value


class Note:
    """Note for storing text content with tags.

    Attributes:
        id (int)
        body (Field)
        tags (list[Tag])

    Args:
        body: Note text content.
        tags: Optional list of tags to add when creating note.
    """

    def __init__(self, body: str, tags: list[str] = None):
        self.id = None
        self.body = Body(body)
        self.tags = tags.copy() if tags else []

    def __str__(self):
        tags = ', '.join(self.tags)
        return f"Note #{self.id}: {self.body[:50]}{'...' if len(self.body) > 50 else ''} [{tags}]"

    def set_body(self, value: str):
        """Set body text for the note.

        Args:
            value (str): String value of the body to set.
        """
        self.body = Body(value)

    def add_tag(self, value: str) -> bool:
        """Add tag to the list avoiding the duplicates.

        Args:
            value (str): String value of the tag to add.

        Raises:
            InvalidTagFormatError: If is empty or has invalid format.

        Returns:
            bool: True if tag was added. False if skipped duplicate.
        """
        if value in self.tags:
            return False

        self.tags.append(Tag(value))
        return True

    def remove_tag(self, value: str):
        """Remove tag from the list.

        Args:
            tag (str): String value of the tag to remove.

        Raises:
            ValueError: If tag not found.
        """
        self.tags.remove(value)

    def find_tag(self, value: str) -> Tag | None:
        """Return tag record by string.

        Args:
            value (str): String value of the tag to find.

        Returns:
            Tag or None: Object if found. None otherwise.
        """
        try:
            return self.tags[self.tags.index(value)]
        except (ValueError, IndexError):
            return None

    def replace_tag(self, old_value: str, new_value: str):
        """Replace existing tag with new value.

        Args:
            old_value (str): String value of the existing tag.
            new_value (str): String value of the new tag.

        Raises:
            ValueError: If value lookup fails
            IndexError: If item disappears before referencing.
            InvalidTagFormatError: If is empty or has invalid format.
        """
        self.tags[self.tags.index(old_value)] = Tag(new_value)


class NoteBook(UserDict):
    """NoteBook dict for note storage and management."""

    id_iter = itertools.count()
    last_id = 0

    @classmethod
    def reset_id(cls, value: int = 1):
        """Reset id_iter state.

        Args:
            value (int): Starting value for iteration.
        """
        cls.id_iter = itertools.count(value)
        cls.last_id = value

    def add_note(self, note: Note):
        """Add new Note to the dict.

        Args:
            note (Note): New Note object to add.
        """
        note.id = next(self.id_iter)
        NoteBook.last_id = note.id
        self.data[note.id] = note

    def delete_note(self, id_: int):
        """Delete Note from the dict.

        Args:
            id_ (int): Key of the Note to delete.

        Raises:
            KeyError: If key not found during referencing.
        """
        del self.data[id_]

    def update_note(self, id_: int, body: str):
        """Update Note body.

        Args:
            id_ (int): Existing key of the Note to update.
            body (str): New body text.

        Raises:
            KeyError: If key not found during referencing.
        """
        self.data[id_].set_body(body)

    def get_note(self, id_: int = None) -> Note | None:
        """Return Note by ID.

        Args:
            id_ (str): Key of the Note to get.

        Returns:
            Note or None: Object if found. None otherwise.
        """
        return self.data.get(id_)

    def find(self, search_value: str = None) -> dict:
        """Find all Notes matching search value.

        Searchable fields: body, tags.

        Args:
            search_value (str): Matching value to find.

        Returns:
            list[Note]: List of matched Notes.
        """
        notes = {}
        search_value = search_value.lower()
        for note in self.values():
            if (
                search_value in note.body.value.lower() or
                any(search_value in tag.value.lower() for tag in note.tags)
            ):
                notes[note.id] = note
        return notes
