"""Various functions to display text in TENENBAUM.

fit_text - display a block of text within a certain width
clean_text - clear away any whitespaces from text before running fit_text
center - run clean_text before centering a block of text
left_align - run clean_text before left aligning a block of text
vert_align - push a block of text to the top of specified number of lines
"""


def fit_text(text, line_width):
    """Return a list of lines, limiting the length of each line to
    the given line_width.
    """

    # Including the empty string cleans up the if-else statement
    text_lines = ['']

    # create a list of lines, where the words fit the line width
    i = 0
    while len(text) > 0:
        word = text[0]
        line = text_lines[i]

        string_length = len(line) + 1 + len(word)

        if (string_length <= line_width) and (len(line) > 0):
            text_lines[i] += " " + text.pop(0)
        else:
            text_lines.append(text.pop(0))
            i += 1

    # get rid of initial empty entry
    return text_lines[1:]


def clean_text(text, line_width):
    """Clear leading/trailing whitespace and line breaks,
    return list of lines with length of line_width,
    including trailing whitespaces
    """

    # Split the string text at each line break
    text_lines = text.split("\n")

    # Remove trailing and leading whitespace from each line
    stripped_lines = []
    for line in text_lines:
        stripped_lines.append(line.strip())

    stripped_text = " ".join(stripped_lines)

    words = stripped_text.split(" ")

    # create a list of lines, where the words fit the line width
    clean_lines = fit_text(words, line_width)

    return clean_lines


def center(text, line_width):
    """Return a list of lines, centered to the given line_width,
    including whitespace to fill the line to the left and right
    """

    clean_lines = clean_text(text, line_width)
    centered_lines = []

    for line in clean_lines:
        left_indent = " " * ((line_width - len(line)) // 2)
        right_indent = " " * (line_width - (len(line) + len(left_indent)))
        centered_lines.append(left_indent + line + right_indent)

    if len(centered_lines) == 1:
        return centered_lines[0]
    else:
        return centered_lines


def left_align(text, line_width):
    """Return a list of lines, left aligned in the given line_width,
    including whitespace to fill the line on the right
    """

    clean_lines = clean_text(text, line_width)
    left_aligned_lines = []

    for line in clean_lines:
        right_indent = " " * (line_width - len(line))
        left_aligned_lines.append(line + right_indent)

    if len(left_aligned_lines) == 1:
        return left_aligned_lines[0]
    else:
        return left_aligned_lines


def vert_align(text, line_width, list_height):
    """Takes list of lines.
    Returns a list of lines. Lines with content begin at index 0, with
    empty strings at the end of the list, resulting in a len(list) equal
    to the given list_height.
    """

    if len(text) >= list_height:
        return text

    else:
        lines = []
        line_count = 0

        for line in text:
            lines.append(line)
            line_count += 1

        for empty_line in range(list_height - line_count):
            empty_line = " " * line_width
            lines.append(empty_line)

        return lines
