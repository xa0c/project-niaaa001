# Contacts & Notes CLI

A cross‑platform, terminal‑native personal organizer. Manage contacts (“Records”), their properties and phone numbers, keep tagged notes, search everything, and get birthday reminders—all from a fast, forgiving CLI. Data lives in `store.bin`, with on‑the‑fly switching between encrypted and plain pickle formats.

---

## Highlights

- *Records + properties:* address, birthday, email, photo; multiple phones per record.
- *Notes + tags:* create, rename, delete; tag add/replace/remove; sort notes by tags.
- *Search & reminders:* keyword search across records/notes, upcoming birthdays window.
- *On‑the‑fly storage mode:* toggle between *encrypted‑pickle* and *non‑encrypted‑pickle*; file is re‑serialized on save.
- *Command guessing:* understands synonyms and partial letter‑matches (type less, get more).
- *Two run modes:* interactive shell (multiline session) or one‑shot command execution.
- *TUI niceties:* rich, colored output (Rich), optional ASCII previews for photos (ascii‑magic + Pillow).
- *Secure crypto:* Fernet from the `cryptography` package for encryption.

---

## Installation

**Prereqs (all OS):**

- Python 3.10+ and `pip`
- Git (to clone from GitHub)
- A terminal with UTF‑8 support

**Get the code (from GitHub):**

[https://github.com/xa0c/project-niaaa001/](https://github.com/xa0c/project-niaaa001/)

> The repository includes a `requirements.txt`.

### Linux / macOS

```
# Create and activate a virtual environment:
python3 -m venv .venv
. .venv/bin/activate

# Upgrade pip and install deps:
pip install -U pip
pip install -r requirements.txt

# Run the app (examples below in “Usage”).
```

> If your distro lacks prebuilt wheels for `cryptography`, install system headers (e.g., OpenSSL/ffi dev packages) using your package manager.

### Windows (PowerShell)

```
# Create and activate a virtual environment:
py -3 -m venv .venv
.venv\Scripts\Activate.ps1

# Upgrade pip and install deps:
python -m pip install -U pip
pip install -r requirements.txt

# Run the app (examples below in “Usage”).
```

---

## Usage

### Interactive CLI

```
python path\to\main.py

# You’ll get an interactive prompt; type commands like:
help
new-record Alice
phone Alice 0999999999
exit
```

### One‑shot commands

```
# Run a single command and exit (use quotes for multiword values)
python -m <package_module> new-record "John Doe"
python -m <package_module> birthday "John Doe" 01.02.2003
python -m <package_module> birthdays 14
```

---

## Command reference

The CLI supports the following commands (delete/unset by passing an empty string `""`). Source: in‑app help.

```
Records
	new-record <name>                  Create new Record.
	records                            Display all Records.
	records <name>                     Display one Record.
	records <name> <val>               Rename Record.
	records <name> ""                  Delete Record.

Properties (address, birthday, email, photo)
	<property> <rec_name>              Show Record's property.
	<property> <rec_name> <val>        Set Record's property.
	<property> <rec_name> ""           Unset Record's property.

Phones
	phone <rec_name>                   Show all phones.
	phone <rec_name> <val>             Add new phone to the Record.
	phone <rec_name> <val> <new>       Replace phone in the Record.
	phone <rec_name> <val> ""          Delete phone from the Record.

Notes
	new-note <val>                     Create new Note.
	notes                              Display all Notes.
	notes <id>                         Display one Note.
	notes <id> <val>                   Rename Note.
	notes <id> ""                      Delete Note.

Tags
	tag <note_id>                      Show all tags.
	tag <note_id> <val>                Add new tag to the Note.
	tag <note_id> <val> <new>          Replace tag in the Note.
	tag <note_id> <val> ""             Delete tag from the Note.

Search / Filter
	find-records <val>                 Search inside Records by keyword.
	find-notes <val>                   Search inside Notes by keyword.
	sort-by-tags <val>                 Sort all Notes by Tags.
	birthdays [<days>]                 Show congratulations window (default 7 days).

System
	help                               Print help.
	hello                              Print “hello”.
	encryption <on|off>                Control storage encryption.
	exit | close                       Save and quit.
```

---

## Storage & encryption

- **File:** `store.bin` in your working directory (or where configured by your repo).
- **Modes:** plain pickle or Fernet‑encrypted pickle; switch anytime with `encryption on` / `encryption off`.
- **Crypto:** powered by `cryptography.fernet`. Keep your encryption key material secure (your local config.json handles the key).

---

## Command guessing

Type shorter, not harder. The app resolves commands by:

- **Synonyms** (common alternative names).
- **Partial** letter‑matching (unique prefixes).

Examples (illustrative):

- `rec` → `records`
- `ew-zec` → `new-record`
- `reate` → `new-record`
- `bday` → `birthdays`

If a prefix is ambiguous, the CLI will prompt or pick the closest match based on its synonym map.

---

## Examples

```
# Create a record and set properties
new-record Alice
address Alice "42 Galaxy Way"
birthday Alice 01.02.2003
email Alice alice@example.com
phone Alice 0999999999
photo Alice http://example.com/alice.jpg
photo Alice ./alice.jpg

# Work with notes and tags
new-note "Buy milk and tea"
notes
tag 1 urgent
sort-by-tags urgent

# Search and reminders
find-records "galaxy way"
find-notes milk
birthdays 365

# Toggle encryption and save
encryption on
exit
```

---

## Tech stack

- `cryptography.fernet` — symmetric encryption for `store.bin`
- `rich` — colored, structured terminal output
- `ascii-magic`, `Pillow` — optional ASCII rendering and image handling

---

## Contributing

Issues and PRs welcome on GitHub.
