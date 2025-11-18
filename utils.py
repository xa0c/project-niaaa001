from ascii_magic import AsciiArt


def is_leap_year(year: int) -> bool:
    """Check if provided year is a leap year.

    Args:
        year (int): Year to check.

    Returns:
        bool: True if a leap year. False otherwise.
    """
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0


def hex_to_rgb(val: str) -> tuple[int, int, int]:
    """Convert hex color string into RGB tuple.

    Args:
        val (str): Hex color string.

    Returns:
        tuple[int, int, int]: RGB tuple.
    """
    return int(val[1:3], 16), int(val[3:5], 16), int(val[5:7], 16)


def get_truecolor_string(art: AsciiArt, **kwargs) -> str:
    """Return bf/fg-colored ASCII string for AsciiArt object.

    Args:
        art (AsciiArt): AsciiArt object.

    Returns:
        str: ASCII string representation of the image.
    """
    char_rows = art.to_character_list(full_color=True, **kwargs)

    output = ""
    for row in char_rows:
        for cell in row:
            r, g, b = hex_to_rgb(cell["full-hex-color"])
            # Foreground: `\x1b[38;2;`. Background: `\x1b[48;2;`
            output += f"\x1b[48;2;{r};{g};{b}m\x1b[38;2;{r};{g};{b}m{cell['character']}"
        # Reset all after final char of each row
        output += "\x1b[0m\n"
    return output
