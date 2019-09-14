"""TENENBAUM (v0.4 - very much in progress)

v0.4 Features:
- Conditional room descriptions for FillerRoom based on .fullname


v0.3 Features:
- Cleaned up Room.get_description()
- Added individual room descriptions (still writing)
- Added conditional room description for House


v0.2 Features:
- Included multi-line descriptions with line breaks


v0.1 Features:
- Mostly complete structure for:
    - Game Engine, running the game
    - Game Window, drawing the screen
    - Game Map, with info about individual rooms and tile relationships
    - Individual Rooms, with position, items, other related info
- Input interpretation, check for valid actions
- Interactable items -- axe, map, tree
- Movement from room to room
- Updating story box, map graphics, current room name, current time
- Displaying help screen when you command 'help'


To-Do:

[]    Complete Rooms:
      - write descriptions for each room, essentially write actual game
      - create mini-games for willow tree/snowman, with time/map reward
      - define get_description() based on:
          - relevant statuses
          - results of special actions during this turn
          - number of times visited
          - random choice between possible options
      - complete Midnight(Room):
              - enter this room once turns_left is 0 (midnight)
              - determine the end of the game
              - play an animation on loop to finish, depending on ending

              Three Possible Endings:
              1. Best: You get a Christmas tree on time
              2. Good: You get a Christmas tree, but don't get home
              3. Bad: You do not get a Christmas tree
                 - You get arrested for cutting down a neighbor's tree
"""

import os
import random

import text_display
import read_input
from read_input import process

INVALID_STATEMENT = "Sorry, try a different command."


class Engine(object):
    """The Engine runs the game.

    .story_display - lines that make up the display within the story box.

    play() - draw the screen, take input, register updated info
    take_action() - take processed input, run script based on action
    get_story_display() - set last input and current room description
        to display
    """

    def __init__(self):
        self.player_inventory = []
        self.turns_left = 20
        self.story_display = [
            text_display.left_align("", 46),
            text_display.left_align("", 46),
            text_display.left_align("", 46),
            text_display.left_align("", 46),
            text_display.left_align("", 46),
            text_display.left_align("", 46),
            text_display.left_align("", 46),
            text_display.left_align("", 46),
            text_display.left_align("", 46),
            text_display.left_align("", 46),
            text_display.left_align("", 46),
            text_display.left_align("", 46),
            text_display.left_align("", 46),
            text_display.left_align("", 46),
            text_display.left_align("", 46)
        ]

    def play(self, window, map):
        """Run this as a main loop, collecting input, carrying out actions"""

        # Load current room details
        map.enter_room(self)

        # Draw the room
        window.draw(self, map)

        # Take simple input for title screen only, otherwise process it.
        if map.current_room.nickname == '':
            input("  Press ENTER to start the game! ")
            map.change_current_room('C3')
            last_action = "Our story begins..."
        else:
            last_action = self.take_action(window, map)

        # Refresh map/display data for next loop
        map.get_tile_images(self)
        description = map.current_room.get_description()
        self.get_story_display(last_action, description)

    def act_help(self, window, map, object):
        """Display a help screen, press enter to return to game"""

        help_subtitle = "This is a text-based adventure!"

        help_text = """Your mission is to get a tree before Santa
        arrives at midnight.  Every step you take, every move you
        make, the clock will tick, so be prudent!  To get around, try
        entering commands like "Move north!" or "Pick up the axe, dummy!"
        and see what you're able to do.
        """

        if object == '':
            self.get_story_display(help_subtitle, help_text)
            window.draw(self, map)
            action_statement = "You're right back in the action!"
        else:
            action_statement = INVALID_STATEMENT

        input("  Press ENTER to return to the game! ")

        return action_statement

    def act_move(self, window, map, direction):
        """change tiles by picking a cardinal directions"""

        # Define statements for running into a wall/progressing
        wall_statements = {
            'n': 'You cannot go any further North!',
            'e': 'You cannot go any further East!',
            's': 'You cannot go any further South!',
            'w': 'You cannot go any further West!'
            }
        progress_statements = {
            'n': [
                "You went North.",
                "You wandered North.",
                "You moved onward, to the North."
                ],
            'e': [
                "You went East.",
                "You wandered East.",
                "You moved onward, to the East."
                ],
            's': [
                "You went South.",
                "You wandered South.",
                "You moved onward, to the South."
                ],
            'w': [
                "You went West."
                "You wandered West.",
                "You moved onward, to the West."
                ]
            }

        # Run if objeect of input is 'n', 's', 'e', or 'w'
        if direction in progress_statements.keys():

            # Set the new room based on input's object
            new_room = map.current_room.neighbors[direction]

            # mMve to new room if it exists
            if new_room != None:
                map.change_current_room(new_room)
            else:
                return wall_statements[direction]

            # Count this as a turn if successful
            self.turns_left -= 1

            # Set the statement based on the input's object
            action_statement = random.choice(progress_statements[direction])

        else:
            action_statement = INVALID_STATEMENT

        return action_statement

    def act_take(self, window, map, item):
        """Take an item from the room you are in."""

        if item in map.current_room.items:
            # Remove item from room's items list, add to player inventory
            taken_item = map.current_room.items.pop()
            self.player_inventory.append(taken_item)
            action_statement = f"You took the {taken_item}."

            # Count this as a turn if you took an item
            self.turns_left -= 1
        else:
            action_statement = INVALID_STATEMENT

        return action_statement

    def act_cut(self, window, map, object):
        """Cut down the tree, takes 2-5 swings (5 mins/swing)"""

        requirements_met = 'axe' in self.player_inventory and 'tree' in map.current_room.items

        if object == 'tree' and requirements_met:
            # Choose random number of swings it takes to cut tree
            number_of_swings = random.randint(2,5)

            felled_tree = map.current_room.items.pop()
            self.player_inventory.append(felled_tree)
            action_statement = f"After {number_of_swings} swings of the axe, the tree fell!"

            # Count this as a turn per swing
            self.turns_left -= number_of_swings

        else:
            action_statement = INVALID_STATEMENT

        return action_statement

    def take_action(self, window, map):
        """from processed input, run scripts based on given verb and object"""

        # Get processed input
        processed_input = process(window.input_char)

        verb = processed_input['verb']
        object = processed_input['object']

        # Check for VALID input

        if verb == 'help':
            action_statement = self.act_help(window, map, object)

        elif verb == 'move':
            action_statement = self.act_move(window, map, object)

        elif verb == 'take':
            action_statement = self.act_take(window, map, object)

        elif verb == 'cut':
            action_statement = self.act_cut(window, map, object)

        else:
            action_statement = INVALID_STATEMENT

        return action_statement

    def get_story_display(self, action_statement, description):
        """get summary of last action, followed by room description
        add any line breaks to separate passages in the description
        align it left & vertically, assign it to self.story_display
        """

        story_lines = [
            text_display.left_align(action_statement, 46),
            text_display.left_align('', 46)
            ]

        for p in range(len(description)):
            passage = description[p]

            # Using the length of the object, determine wheter str or list
            # If string, add the line, if list, add each line
            if len(passage) > 7 and len(passage) < 78:
                story_lines.append(text_display.left_align(passage, 46))
            else:
                for line in text_display.left_align(passage, 46):
                    story_lines.append(line)

            story_lines.append(text_display.left_align('', 46))

        all_lines = text_display.vert_align(story_lines, 46, 15)

        self.story_display = all_lines

        return None


class Window(object):
    """The Window contains the main parameters for the Terminal window,
        as well as the visuals for the game's display.
    """

    def __init__(self, height, width, font_size):
        """height and width are defined by number of characters"""
        self.height = height
        self.width = width
        self.font_size = font_size
        self.input_char = "  > "

    def draw(self, engine, map):
        """Print the game screen according to status of given map,
            at the time the function was called on Window.
        """

        # Set Terminal window parameters
        os.system('osascript -e \'tell app "System Events" to tell process "Terminal" to set frontmost to true\'')
        os.system(f'osascript -e \'tell app "Terminal" to set font size of first window to "{self.font_size}"\'')
        os.system(f'printf "\e[8;{self.height};{self.width}t"')

        # Set time of day, as displayed on screen
        times_of_day = [
        '10:00 PM','10:05 PM','10:10 PM','10:15 PM','10:20 PM','10:25 PM',
        '10:30 PM','10:35 PM','10:40 PM','10:45 PM','10:50 PM','10:55 PM',
        '11:00 PM','11:05 PM','11:10 PM','11:15 PM','11:20 PM','11:25 PM',
        '11:30 PM','11:35 PM','11:40 PM','11:45 PM','11:50 PM','11:55 PM',
        'MIDNIGHT'
        ]
        time_of_day = text_display.center(times_of_day[20 - engine.turns_left], 8)

        # Temporarily set brackets around the current room's map_image
        for location in map.tile_images:
            if map.tiles[location].room == map.current_room:
                map.tile_images[location] = '[' + map.tile_images[location][1] + ']'
            else:
                pass

        game_screen = """
          .------------------------------------------------.   .-------------------.
          | {} |   |{}|{}|{}|{}|{}|
          |                                                |   |---+---+---+---+---|
          | {} |   |{}|{}|{}|{}|{}|
          | {} |   |---+---+---+---+---|
          | {} |   |{}|{}|{}|{}|{}|
          | {} |   |---+---+---+---+---|
          | {} |   |{}|{}|{}|{}|{}|
          | {} |   |---+---+---+---+---|
          | {} |   |{}|{}|{}|{}|{}|
          | {} |   '-------------------'
          | {} |
          | {} |      -- LOCATION --
          | {} |    {}
          | {} |
          | {} |        -- TIME --
          | {} |         {}
          | {} |
          '------------------------------------------------'
        """.format(
            text_display.left_align(map.current_room.fullname, 46),
                map.tile_images['A1'], map.tile_images['A2'],
                map.tile_images['A3'], map.tile_images['A4'],
                map.tile_images['A5'],
            engine.story_display[0],
                map.tile_images['B1'], map.tile_images['B2'],
                map.tile_images['B3'], map.tile_images['B4'],
                map.tile_images['B5'],
            engine.story_display[1],
            engine.story_display[2],
                map.tile_images['C1'], map.tile_images['C2'],
                map.tile_images['C3'], map.tile_images['C4'],
                map.tile_images['C5'],
            engine.story_display[3],
            engine.story_display[4],
                map.tile_images['D1'], map.tile_images['D2'],
                map.tile_images['D3'], map.tile_images['D4'],
                map.tile_images['D5'],
            engine.story_display[5],
            engine.story_display[6],
                map.tile_images['E1'], map.tile_images['E2'],
                map.tile_images['E3'], map.tile_images['E4'],
                map.tile_images['E5'],
            engine.story_display[7],
            engine.story_display[8],
            engine.story_display[9],
            engine.story_display[10],
                text_display.center(map.current_room.nickname, 18),
            engine.story_display[11],
            engine.story_display[12],
            engine.story_display[13],
                time_of_day,
            engine.story_display[14]
        )

        # Clear screen, print window
        self.clear()

        for line in game_screen.split('\n'):
            # Compensate for indentation in game_screen
            print(line[8:])

        # Reset current room's map image, without brackets
        for location in map.tile_images:
            if map.tiles[location].room == map.current_room:
                map.tile_images[location] = ' ' + map.tile_images[location][1] + ' '
            else:
                pass

    def clear(self):
        os.system('clear')


class Map(object):
    """The Map contains information about the organization of Rooms
        and Tiles.
    """

    def __init__(self, current_room, engine):

        self.current_room = current_room

        # dictionary of map rooms
        #     key = Tile.room.location,
        #     value = Tile.room
        self.tiles = self.new_map()

        # dictionary of map tile images,
        #     key = Tile.room.location,
        #     value = Tile.room.map_image OR "###" if not yet visited
        self.tile_images = self.get_tile_images(engine)

    def new_map(self):
        """Generate a list of Tiles, A1-E5.
        Put the House in the center tile, C3.
        Populate the tiles randomly from list of rooms.
        """

        map_tiles = {
        'A1': Tile(
            'A1',
            {'n': None, 'e': 'A2', 's': 'B1', 'w': None},
            None),
        'A2': Tile(
            'A2',
            {'n': None, 'e': 'A3', 's': 'B2', 'w': 'A1'},
            None),
        'A3': Tile(
            'A3',
            {'n': None, 'e': 'A4', 's': 'B3', 'w': 'A2'},
            None),
        'A4': Tile(
            'A4',
            {'n': None, 'e': 'A5', 's': 'B4', 'w': 'A3'},
            None),
        'A5': Tile(
            'A5',
            {'n': None, 'e': None, 's': 'B5', 'w': 'A4'},
            None),
        'B1': Tile(
            'B1',
            {'n': 'A1', 'e': 'B2', 's': 'C1', 'w': None},
            None),
        'B2': Tile(
            'B2',
            {'n': 'A2', 'e': 'B3', 's': 'C2', 'w': 'B1'},
            None),
        'B3': Tile(
            'B3',
            {'n': 'A3', 'e': 'B4', 's': 'C3', 'w': 'B2'},
            None),
        'B4': Tile(
            'B4',
            {'n': 'A4', 'e': 'B5', 's': 'C4', 'w': 'B3'},
            None),
        'B5': Tile(
            'B5',
            {'n': 'A5', 'e': None, 's': 'C5', 'w': 'B4'},
            None),
        'C1': Tile(
            'C1',
            {'n': 'B1', 'e': 'C2', 's': 'D1', 'w': None},
            None),
        'C2': Tile(
            'C2',
            {'n': 'B2', 'e': 'C3', 's': 'D2', 'w': 'C1'},
            None),
        'C3': Tile(
            'C3',
            {'n': 'B3', 'e': 'C4', 's': 'D3', 'w': 'C2'},
            None),
        'C4': Tile(
            'C4',
            {'n': 'B4', 'e': 'C5', 's': 'D4', 'w': 'C3'},
            None),
        'C5': Tile(
            'C5',
            {'n': 'B5', 'e': None, 's': 'D5', 'w': 'C4'},
            None),
        'D1': Tile(
            'D1',
            {'n': 'C1', 'e': 'D2', 's': 'E1', 'w': None},
            None),
        'D2': Tile(
            'D2',
            {'n': 'C2', 'e': 'D3', 's': 'E2', 'w': 'D1'},
            None),
        'D3': Tile(
            'D3',
            {'n': 'C3', 'e': 'D4', 's': 'E3', 'w': 'D2'},
            None),
        'D4': Tile(
            'D4',
            {'n': 'C4', 'e': 'D5', 's': 'E4', 'w': 'D3'},
            None),
        'D5': Tile(
            'D5',
            {'n': 'C5', 'e': None, 's': 'E5', 'w': 'D4'},
            None),
        'E1': Tile(
            'E1',
            {'n': 'D1', 'e': 'E2', 's': None, 'w': None},
            None),
        'E2': Tile(
            'E2',
            {'n': 'D2', 'e': 'E3', 's': None, 'w': 'E1'},
            None),
        'E3': Tile(
            'E3',
            {'n': 'D3', 'e': 'E4', 's': None, 'w': 'E2'},
            None),
        'E4': Tile(
            'E4',
            {'n': 'D4', 'e': 'E5', 's': None, 'w': 'E3'},
            None),
        'E5': Tile(
            'E5',
            {'n': 'D5', 'e': None, 's': None, 'w': 'E4'},
            None)
        }

        # Set middle tile to House
        map_tiles['C3'].room = House('My House', 'A Lovely Little House', ' H ', ['Something!'])

        # Set rest of tiles to a random room
        map_rooms = [
            Shed('Old Shed', 'Old Shed Full of Machinery', ' S ', ['axe']),
            Barn('Red Barn', 'Giant Red Barn', ' B ', ['map']),
            FrozenPond('Frozen Pond', 'Deep Pond, Frozen Solid', ' P ', []),
            Snowman("Snowman's Land", 'A Snowman Stands Before You', ' 8 ', []),
            NeighborTree("A Tree", "A Tree, Just Beyond a Fence", ' T ', ['tree']),
            NeighborTree("A Tree", "A Tree, Just Beyond a Fence", ' T ', ['tree']),
            ChristmasTree("A Tree", "A Stunning Pine Tree", ' T ', ['tree']),
            ChristmasTree("A Tree", "A Beautiful Pine Tree", ' T ', ['tree']),
            ChristmasTree("A Tree", "A Gorgeous Pine Tree", ' T ', ['tree']),
            WillowTree("A Tree", "An Enormous Willow Tree", ' W ', ['tree']),
            FillerRoom("A Hillside", "A Snow-Covered Hill", '   ', []),
            FillerRoom("A Hillside", "A Rocky Hill", '   ', []),
            FillerRoom("A Forest", "A Deep Forest of Birch and Oak", '   ', []),
            FillerRoom("A Forest", "A Sparse Patch of Elms", '   ', []),
            FillerRoom("A Trail", "A Gravel Road", '   ', []),
            FillerRoom("A Trail", "A Shallow Path Through The Snow", '   ', []),
            FillerRoom("A Garden", "A Quiet Garden Blanketed In Snow", '   ', []),
            FillerRoom("A Garden", "A Neighbor's Garden", '   ', []),
            FillerRoom("A Field", "A Field Of Wildflowers", '   ', []),
            FillerRoom("A Field", "An Abandoned Corn Field", '   ', []),
            FillerRoom("A Junkyard", "Heaps Of Junk, Whitewashed In The Snow", '   ', []),
            FillerRoom("A Dirt Road", "A Tunnel Of Branches Over A Dirt Road", '   ', []),
            FillerRoom("A Treehouse", "Your Childhood Treehouse", '   ', []),
            FillerRoom("A Bench", "Wooden Bench, Overlooking A Hill", '   ', [])
        ]
        for tile in map_tiles:

            # Skip any tiles already containing a room
            if map_tiles[tile].room == None:
                random_room = map_rooms.pop(random.randint(0, len(map_rooms) - 1))

                # Assign room's neighbors to assigned tile's neighbors
                random_room.neighbors = map_tiles[tile].neighbors

                # Assign tile's room to room
                map_tiles[tile].room = random_room
            else:
                pass

        return map_tiles

    def enter_room(self, engine):
        """Set relevant variables to new values, given the new room
        you are entering.
        """
        self.current_room.times_visited += 1
        self.get_tile_images(engine)

    def get_tile_images(self, engine):
        """Get the image for each tile, based on # of times visited"""

        tile_images = {}

        # Hide tile's map image if has not yet been visited
        for tile in self.tiles:
            if self.tiles[tile].room.times_visited == 0 and 'map' not in engine.player_inventory:
                tile_images[tile] = "###"

            else:
                tile_images[tile] = self.tiles[tile].room.map_image

        self.tile_images = tile_images

        return tile_images

    def change_current_room(self, new_room_location):
        self.current_room = self.tiles[new_room_location].room
        self.current_room.neighbors = self.tiles[new_room_location].neighbors


class Tile(object):
    """A Tile has:
        .location - coordinates, eg. 'A1'
        .neighbors - dictionary, keys 'n', 'e', 's', 'w', vals 'A1'...
        .room - assigned during new_map(), Room object
    """


    def __init__(self, location, neighbors, room):
        self.location = location
        self.neighbors = neighbors
        self.room = room


class Room(object):
    """Contains information about each room, including:
        .nickname - appears under '-- LOCATION --'
        .fullname - appears at the top of story box
        .map_image - three character display for map
        .description - based on current status, description of room
        .neighbors - dictionary of neighboring tiles, assigned
            during Map.new_map()
        .times_visited - increments everytime you enter the room
    """

    def __init__(self, nickname, fullname, map_image, items):
        self.times_visited = 0
        self.nickname = nickname
        self.fullname = fullname
        self.map_image = map_image
        self.neighbors = {}
        self.items = items
        self.description = self.get_description()

    def get_description(self):
        """Get description based on Map status"""

        ## OVERRIDE CODE HERE TO DEFINE SPECIFIC TRIGGERS
        description = [
            """This Room is Not Configured Yet.""",
            """It must be at least two lines long, and even more preferable
            for testing, if it has at least one fairly long line.
            """]

        return description


class House(Room):

    def get_description(self):

        if self.times_visited == 0:
            description = [
                """Christmas is your absolute favorite holiday.""",
                """It's silly, but every year you love looking forward to
                wrapping presents, singing carols, hanging ornaments
                on the--""",
                """THE TREE!""",
                """You forgot to get a tree!
                How is this possible? No tree and only two hours
                'til Christmas! Better get one before Santa comes!"""
                ]
        elif 'tree' not in main_engine.player_inventory:
            description = [
            """This is your house!""",
            """My, it's lovely."""
            ]
        else:
            description = [
            """You found the tree! Good job."""
            ]

        return description

class Shed(Room):

    def get_description(self):

        description = [
            """This is the shed."""
            ]

        return description

class Barn(Room):

    def get_description(self):

        description = [
            """This is the barn."""
            ]

        return description

class FrozenPond(Room):

    def get_description(self):

        description = [
            """This is the frozen pond."""
            ]

        return description

class Snowman(Room):

    def get_description(self):

        description = [
            """This is the snowman's land."""
            ]

        return description

class NeighborTree(Room):

    def get_description(self):

        description = [
            """This is a neighbor's tree."""
            ]

        return description

class ChristmasTree(Room):

    def get_description(self):

        description = [
            """This is a proper Christmas tree!"""
            ]

        return description

class WillowTree(Room):

    def get_description(self):

        description = [
            """This is a beautiful willow tree."""
            ]

        return description

class FillerRoom(Room):

    def get_description(self):

        if self.fullname == "A Snow-Covered Hill":
            description = [
            """Enter description here."""
            ]

        elif self.fullname == "A Rocky Hill":
            description = [
            """Enter description here."""
            ]

        elif self.fullname == "A Deep Forest of Birch and Oak":
            description = [
            """Enter description here."""
            ]

        elif self.fullname == "A Sparse Patch of Elms":
            description = [
            """Enter description here."""
            ]

        elif self.fullname == "A Gravel Road":
            description = [
            """Enter description here."""
            ]

        elif self.fullname == "A Shallow Path Through The Snow":
            description = [
            """Enter description here."""
            ]

        elif self.fullname == "A Quiet Garden Blanketed In Snow":
            description = [
            """Enter description here."""
            ]

        elif self.fullname == "A Neighbor's Garden":
            description = [
            """Enter description here."""
            ]

        elif self.fullname == "A Field Of Wildflowers":
            description = [
            """Enter description here."""
            ]

        elif self.fullname == "An Abandoned Corn Field":
            description = [
            """Enter description here."""
            ]

        elif self.fullname == "Heaps Of Junk, Whitewashed In The Snow":
            description = [
            """Enter description here."""
            ]

        elif self.fullname == "A Tunnel Of Branches Over A Dirt Road":
            description = [
            """Enter description here."""
            ]

        elif self.fullname == "Your Childhood Treehouse":
            description = [
            """Enter description here."""
            ]

        elif self.fullname == "Wooden Bench, Overlooking A Hill":
            description = [
            """Enter description here."""
            ]

        return description


class MidnightScreen(Room):
    pass

class TitleScreen(Room):
    pass

# INITIALIZE VARIABLES
main_engine = Engine()
main_window = Window(23, 78, 16)
title_screen = TitleScreen('', 'TENENBAUM: The Game', '   ', [])
midnight_screen = MidnightScreen('Midnight', 'Christmas Morning', '   ', [])
main_map = Map(title_screen, main_engine)

# MAIN LOOP
while True:
    main_engine.play(main_window, main_map)
