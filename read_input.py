"""Function to process input in TENENBAUM

lexicon - list of identifiable verbs and objects, with synonyms
process() - scan input for verbs and objects, return last pair found
"""

lexicon = {
    'verbs':
        {
        'move': ['move', 'go'],
        'take': ['take', 'grab', 'get', 'pick', 'lift', 'look', 'examine'],
        'cut': ['chop', 'cut', 'fell'],
        'help': ['help']
        },
    'objects':
        {
        'n': ['north', 'up'],
        'e': ['east', 'right'],
        's': ['south', 'down'],
        'w': ['west', 'left'],
        'map': ['map'],
        'axe': ['axe'],
        'tree': ['tree']
        }
}

def process(input_char):
    """Read input, extract command words, drop any words/chars to ignore"""

    verb = ""
    object = ""

    raw_input = input(input_char)

    no_spaces = raw_input.split(" ")
    no_hyphens = "-".join(no_spaces).split("-")
    no_periods = ".".join(no_hyphens).split(".")
    no_exclamations = "!".join(no_periods).split("!")
    no_questions = "?".join(no_exclamations).split("?")
    no_amps = "&".join(no_questions).split("&")
    words = no_amps

    for word in words:
        l_word = word.lower()

        for word_type in lexicon['verbs']:
            if l_word in lexicon['verbs'][word_type]:
                verb = word_type
            else:
                pass

        for word_type in lexicon['objects']:
            if l_word in lexicon['objects'][word_type]:
                object = word_type
            else:
                pass

    processed_input = {'verb': verb, 'object': object}

    return processed_input
