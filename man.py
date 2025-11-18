from rich import box, print
from rich.console import Console
from rich.table import Table


def make_section_table(title, commands):
    section = Table(
        title=f"[blue]{title}:[/blue]",
        title_justify="left",
        box=None,
        show_header=False,
        show_edge=False,
        pad_edge=False,
        expand=True,
    )
    section.add_column()
    section.add_column(ratio=1)

    for cmd, desc in commands:
        section.add_row(f"[cyan]{cmd}[/cyan]", f"{desc}")

    section.add_row("")  # spacer
    return section


def render_help() -> str:
    intro = """\
[blue]DESCRIPTION:[/blue]
    This script provides CLI for contacts and notes management.
[blue]NOTES:[/blue]
    Use double quotes if values contain spaces.

[blue]USAGE:[/blue]
"""

    console = Console(record=True, color_system="standard")

    records_collection = make_section_table(
        "Records collection actions",
        [
            ("new-record <name>", "Create new Record."),
            ("records", "Display all Records."),
            ("records <name>", "Display one Record."),
            ("records <name> <val>", "Rename Record."),
            ('records <name> ""   ', "Delete Record."),
        ],
    )

    record_properties = make_section_table(
        "Property (address, birthday, email, photo) actions",
        [
            ("<property> <rec_name>", "Show Record's property."),
            ("<property> <rec_name> <val>", "Set Record's property."),
            ('<property> <rec_name> ""', "Unset Record's property."),
        ],
    )

    record_lists = make_section_table(
        "Phone list actions",
        [
            ("phone <rec_name>", "Show all phones."),
            ("phone <rec_name> <val>", "Add new phone to the Record."),
            ("phone <rec_name> <val> <new>", "Replace phone in the Record."),
            ('phone <rec_name> <val> ""', "Delete phone from the Record."),
        ],
    )

    note_collection = make_section_table(
        "Notes collection actions",
        [
            ("new-note <val>", "Create new Note."),
            ("notes", "Display all Notes."),
            ("notes <id>", "Display one Note."),
            ("notes <id> <val>", "Rename Note."),
            ('notes <id> ""', "Delete Note."),
        ],
    )

    note_lists = make_section_table(
        "Tag list actions",
        [
            ("tag <note_id>", "Show all tags."),
            ("tag <note_id> <val>", "Add new tag to the Note."),
            ("tag <note_id> <val> <new>", "Replace tag in the Note."),
            ('tag <note_id> <val> ""', "Delete tag from the Note."),
        ],
    )

    search = make_section_table(
        "Search/Filter actions",
        [
            ("find-records <val>", "Search inside Record fields by keyword."),
            ("find-notes <val>", "Search inside Notes fields by keyword."),
            ("sort-by-tags <val>", "Sort all Notes by Tags."),
            ("birthdays [ <days> ]", "Show congratulation dates for persons which birthdays are within specified period (7 days by default)."),
        ]
    )

    system = make_section_table(
        "System actions",
        [
            ("help               ", "Prints this message."),
            ("hello              ", "Prints 'hello' message."),
            ("encryption <on|off>", "Control storage encryption."),
            ("exit | close       ", "Saves data into the file and quits application."),
        ]
    )

    # Container table with borders; section tables go in the first (and only) column
    left_container = Table(show_header=False, box=None, show_edge=True, expand=True)
    left_container.add_column()
    for section in (records_collection, record_properties, record_lists):
        left_container.add_row(section)

    right_container = Table(show_header=False, box=None, show_edge=True, expand=True)
    right_container.add_column()
    for section in (note_collection, note_lists, search, system):
        right_container.add_row(section)

    container = Table(show_header=False, box=box.MINIMAL, show_edge=True, expand=False)
    container.add_column(ratio=1)
    container.add_column(ratio=1)
    container.add_row(left_container, right_container)

    with console.capture() as capture:
        console.print(intro)
        console.print(container)

    return capture.get()
