from collections import UserList


class Note:
    """Note for storing text content with tags.

    Structure:
        {
            tags: list[str]
            body: str
        }

    Args:
        body: Note text content.
        tags: Optional list of tags to add when creating note.
    """

    def __init__(self, body: str, tags: list[str] = None):
        self.tags = tags.copy() if tags else []
        self.body = body

    def __str__(self):
        tags_str = ', '.join(self.tags) if self.tags else "no tags"
        return f"Note: {self.body[:50]}{'...' if len(self.body) > 50 else ''} [{tags_str}]"

    def set_body(self, body: str):
        """Set body text for the note.

        Args:
            body (str): String value of the body to set.
        """
        self.body = body

    def add_tag(self, tag: str):
        """Add tag to the list.

        Args:
            tag (str): String value of the tag to add.

        Raises:
            ValueError: If tag is empty or invalid.
        """
        # Validate tag is not empty
        if not tag:
            raise ValueError("Tag cannot be empty.")
        tag = tag.strip()
        # Check for empty string, whitespace only, or quoted empty strings like '' or ""
        if not tag or tag in ("''", '""', "'", '"'):
            raise ValueError("Tag cannot be empty.")
        # Add if not duplicate
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str):
        """Remove tag from the list.

        Args:
            tag (str): String value of the tag to remove.

        Raises:
            ValueError: If tag not found.
        """
        self.tags.remove(tag)

    def replace_tag(self, old_tag: str, new_tag: str):
        """Replace existing tag with new value.

        Args:
            old_tag (str): String value of the existing tag.
            new_tag (str): String value of the new tag.

        Raises:
            ValueError: If old_tag not found or new_tag is empty.
        """
        # Validate new tag is not empty (same validation as add_tag)
        if not new_tag:
            raise ValueError("New tag cannot be empty.")
        new_tag = new_tag.strip()
        if not new_tag or new_tag in ("''", '""', "'", '"'):
            raise ValueError("New tag cannot be empty.")
        index = self.tags.index(old_tag)
        self.tags[index] = new_tag


class NoteBook(UserList):
    """NoteBook list for note storage and management."""

    def add_note(self, note: Note):
        """Add new Note to the list.

        Args:
            note (Note): New Note object to add.
        """
        self.data.append(note)

    def delete_note(self, index: int):
        """Delete Note from the list by index.

        Args:
            index (int): Index of the Note to remove.

        Raises:
            IndexError: If index is out of range.
        """
        del self.data[index]

    def update_note(self, index: int, new_body: str):
        """Update Note body by index.

        Args:
            index (int): Index of the Note to update.
            new_body (str): New body text for the note.

        Raises:
            IndexError: If index is out of range.
        """
        self.data[index].set_body(new_body)

    def find(self, search_text: str) -> list[Note]:
        """Find all notes containing the search text in body or tags.

        Args:
            search_text (str): Text to search for in note body or tags.

        Returns:
            list[Note]: List of notes containing the search text in body or tags.
        """
        search_lower = search_text.lower()
        return [
            note for note in self.data
            if search_lower in note.body.lower() or
            any(search_lower in tag.lower() for tag in note.tags)
        ]
