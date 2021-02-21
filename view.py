import time
import win32console
from typing import Callable
from colorama import init as colorinit


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class View:

    def __init__(self):
        # Grabbing console info
        self.screenbuf_output = self._screen_buffer('output')
        self.screenbuf_input = self._screen_buffer('input')
        self.screenbuf_input_default = self.screenbuf_input.GetConsoleMode()

        # Establishing origin which all drawing will be relative to
        self.cursor_anchor = self._cursor_anchor()

        self.guidestring: str = ""  # UI navigation hint always present at the bottom of the screen
        self.menu_size: int = 5
        # Building out the slots which act as gatekeepers for menu options
        self.slot_titles = ['a', 's', 'd', 'f', 'g']
        self.option_slots = self._init_option_slots()

        # Disabling input echo
        self.input_mirror_disable()
        # Making cursor invisible
        self.screenbuf_output.SetConsoleCursorInfo(100, False)

        # Enabling ANSI escape sequences
        colorinit()

        # Callback functions for communicating with the controller
        self.callbacks = {  # controller populates with functions
            'cb_recipes_get': None
            , 'cb_recipe_select': None
            , 'cb_recipe_deselect': None
            , 'cb_recipe_newrecipe': None
            , 'cb_recipe_newrecipe_additem': None
            , 'cb_recipe_newrecipe_modifyitem': None
            , 'cb_recipe_newrecipe_save': None

            , 'cb_product_search': None

            , 'cb_grocery_buildlist': None
            , ' cb_grocery_moodifylist': None
        }

        # ANSI escape sequences
        self.ansi = {
            'green': '\033[92m'
            , 'gray': '\033[39m'
            , 'clearline': '\033[2K'
        }

    def _screen_buffer(self, option: str):
        """
            Provides the screen buffer of the current console to the caller as a
            PyConsoleScreenBuffer objecet
        """
        if option == 'output':
            return win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
        elif option == 'input':
            return win32console.GetStdHandle(win32console.STD_INPUT_HANDLE)

    def _cursor_anchor(self) -> tuple:
        """
            Returns (x, y) pair of the upper-left-most point of the UI screen. The first line is left blank.
        :return: tuple
        """
        # Retrieving dict of relevant information
        info = self.screenbuf_output.GetConsoleScreenBufferInfo()
        x = info['CursorPosition'].X
        y = info['CursorPosition'].Y

        return x, y

    def _init_option_slots(self) -> dict:
        """
            Instantiates the dictionary that will be used to document the "option slots".  The UI design limits
            the number of options for selection on any given menu to the keys of the dictionary created herein.

            The values are another dictionary that track the cursor position marking the beginning of the screen
            buffer line to which the particular slot belongs.  It also contains the text that is to be displayed.
            This text is update to reflect the current menu context

        :return: dict
        """

        # Complete list of possible generic input values available in the View namespace per screen
        # Note that each screen context is still free to process additional values if it so chooses.

        option_slots = dict()
        for index, slot in enumerate(self.slot_titles):
            # Establishing the line to which each each slot belongs (or vice versa I guess)
            x_coord = self.cursor_anchor[0]
            y_coord = self.cursor_anchor[1] + index + 1
            option_slots[slot] = {'coords': (x_coord, y_coord),
                                  'text': None}
        return option_slots

    def input_mirror_enable(self):
        """
            Toggle mode of the console echo. Based on the win32 API requirements
            https://docs.microsoft.com/en-us/windows/console/setconsolemode
        """
        #val = win32console.ENABLE_ECHO_INPUT + win32console.ENABLE_LINE_INPUT
        self.screenbuf_input.SetConsoleMode(self.screenbuf_input_default)

    def input_mirror_disable(self):
        """
            Turns off input echo.  Input buffer now updates without need for a newline character.
        """
        self.screenbuf_input.SetConsoleMode(0)

    def _update_option_slots(self
                             , options: list[str]
                             , left_index: int
                             , right_index: int) -> dict:

        """
            Slices the given options list based on the passed indices. Then maps them to self.option_slots
            as well as providing a dictionary mapping {<slot_title>: <index>} to caller so that they may
            reference selected item in its scope.

            It is up to caller to bounds check the indices.


            Now also updates the guidestring based on the indices

        :param options:  A list of strings representing the options of the current menu context
        :param left_index:  Bounds the list
        :param right_index:  Bounds the list
        :return: Dictionary mapping each option_slot to the options index it represents.
        """
        # Mapping option strings to self.option_slots
        # Reversing is because we build the menu from the bottom up.
        # Unused space is left blank at the top
        new_options = options[left_index:right_index]
        slot_titles = self.slot_titles[:]
        slot_titles.reverse()
        slot_option_tuples = zip(slot_titles, new_options)

        # Preparing the return dictionary
        ret_dict = dict()
        # Updating the menu context variables which have new display text
        used_titles = []  # Used to update the 'text' field of unused titles to None
        option_index = left_index  # Walks between left_index and right_index
        for tup in slot_option_tuples:
            title = tup[0]
            text = tup[1]
            self.option_slots[title]['text'] = text
            # Updating return variable
            ret_dict[title] = option_index
            # Preparing for next loop
            option_index += 1
            used_titles.append(title)

        # Updating the menu context variables which should now be blank
        for title in self.slot_titles:
            if title not in used_titles:
                self.option_slots[title]['text'] = None

        # Updating the guide string to include paging information
        if left_index > 0:
            self.guidestring += ", [j] to page left"
        if right_index < len(options):
            self.guidestring += ", [k] to page right"

        return ret_dict

    def _mainmenu(self):
        # Building context menu
        options = ['Select Recipes',
                   'Build Recipe',
                   'Build Grocery List',
                   'Place Order']
        # Reversing because the "first" option is the one nearest the bottom
        # and I want Select Recipes at the top
        options.reverse()

        # Establishing guide string
        guidestring = "[key] to make a selection"
        self.guidestring = guidestring

        # The difference here represents the number of menu items displayed per context
        # Really I shouldn't hard code these but I'm getting impatient.
        left_index = 0
        right_index = self.menu_size

        # We don't need to use the returned dictionary because we
        # Don't care about the list entries
        self._update_option_slots(options, left_index, right_index)
        self.print_screen_context()

        actions = {
            'g': self._place_order,
            'f': self._grocery_buildlist,
            'd': self._menu_buildrecipe,
            's': self._recipes_select
        }
        # Beginning input eval loop
        while True:
            user_input = self._input_read()
            if user_input not in actions:
                # Flushing the buffer just in case before re-looping
                self.screenbuf_input.FlushConsoleInputBuffer()
            else:
                # Call the method specified in the actions dictionary
                actions[user_input]()  # NOTE: This is far less readable than in line calls.
                # Returning from deeper menu context
                self._update_option_slots(options, left_index, right_index)
                self.guidestring = guidestring
                self.print_screen_context()

    def _menu_buildrecipe(self):
        # Clearing screen
        self._update_option_slots([], 0, 0)
        self.guidestring = "Enter the name of the recipe: "
        self.print_screen_context()

        # Receiving recipe name
        self.input_mirror_enable()
        recipe_name = input("")

        # Checking valididty
        if not self.callbacks['cb_recipe_newrecipe'](recipe_name):
            self.guidestring = "That is an invalid name. Press (almost) any key to continue."
            self.print_screen_context()
            input("")
            return

        # Building menu options
        options = ['Add ingredient', 'Modify Ingredient', 'Save Recipe']
        options.reverse()
        left_index = 0
        right_index = self.menu_size

        # Beginning menu loop
        user_input: str = ""
        while user_input != 'b':
            # Printing screen
            self.screenbuf_input.FlushConsoleInputBuffer()
            self.guidestring = f'Building "{recipe_name}".  [b] for back'
            self._update_option_slots(options, left_index, right_index)
            self.input_mirror_disable()
            self.print_screen_context()

            # Reading input
            user_input = self._input_read()
            if user_input == 'g':
                self._recipe_newrecipe_save()
                return
            elif user_input == 'f':
                raise NotImplementedErrors("")
                self.callbacks['cb_recipe_newrecipe_modifyitem']
            elif user_input == 'd':
                self._menu_buildrecipe_additem()

    def _menu_buildrecipe_additem(self):
        """
            Asks user for a search term that is then used to search the API
            The menu context then populates with the values
        """
        # Querying user for ingredient name
        self.input_mirror_enable()
        self.guidestring = "What is the name of the ingredient?: "
        self._update_option_slots([], 0, 0)
        self.print_screen_context()
        colloquial_name = input("")

        # Product searching begins
        while True:
            # Asking for API search term
            self.input_mirror_enable()
            self.guidestring = "Enter a search term to submit to the server. Must be at least 3 characters: "
            self._update_option_slots([], 0, 0)
            self.print_screen_context()
            self.screenbuf_input.FlushConsoleInputBuffer()
            search_string = input("")

            # Checking term length
            if len(search_string) < 3:
                continue

            result_list = self.callbacks['cb_product_search'](search_string, self.menu_size)

            # Beginning search result pagination loop
            user_input: str = ""
            while user_input != 'r':
                # Building 'text' strings from given information
                presentable_strings = [self._build_cost_string(result) for result in result_list]

                # Building Menu
                self.input_mirror_disable()
                option_map = self._update_option_slots(presentable_strings, 0, self.menu_size)
                self.guidestring = "[r] retry, [b] return, [j] and [k] to try paginating"
                self.print_screen_context()
                self.screenbuf_input.FlushConsoleInputBuffer()

                # Evaluating input
                user_input = self._input_read()
                if user_input == 'k':
                    result_list = self.callbacks['cb_product_search'](search_string, self.menu_size, 'next')
                elif user_input == 'j':
                    result_list = self.callbacks['cb_product_search'](search_string, self.menu_size, 'previous')
                elif user_input == 'b':
                    return
                elif user_input in option_map:
                    # Select. Now need to get a quantity
                    self._update_option_slots([], 0, 0)  # clearing screen
                    selection = result_list[option_map[user_input]]
                    description = selection['description']
                    self.input_mirror_enable()
                    self.guidestring = f'How many {description}?: '
                    self.screenbuf_input.FlushConsoleInputBuffer()
                    self.print_screen_context()
                    quantity = input("")
                    try:
                        float(quantity)
                        # Adding item to planner and return to the previous menu
                        new_item = {
                            'colloquial_name': colloquial_name
                            , 'product_id': selection['product_id']
                            , 'upc': selection['upc']
                            , 'quantity': quantity
                        }
                        self.callbacks['cb_recipe_newrecipe_additem'](new_item)
                        return
                    except ValueError:
                        continue

    def _build_cost_string(self, product_dict: dict) -> str:
        """
            accepts: {
                'description': <>
                , 'product_id': <>
                , 'size': <>
                , 'price': <>
                , 'upc': <>
            }
            and returns a single string with description + size + price formatted as specified in this method.
        """
        description = product_dict['description'][:50]
        size = product_dict['size']
        price = product_dict['price']

        return f"{description} @@ {price} PER {size}"

    def _recipe_newrecipe_save(self):
        if self.callbacks['cb_recipe_newrecipe_save']():
            self._update_option_slots([], 0, 0)
            self.guidestring = "Successfully saved. Press enter to continue"
            self.print_screen_context()
        else:
            # Error occurred
            self._update_option_slots([], 0, 0)
            self.guidestring = "Error occurred writing new recipe to disk. Press enter to continue"
            self.print_screen_context()
        self.input_mirror_enable()
        input("")

    def _grocery_buildlist(self):
        pass

    def _place_order(self):
        pass

    def _recipes_select(self):

        # Retrieving recipes from the planner
        recipes = self.callbacks['cb_recipes_get']()
        # Establishing recipe navigation variables
        left_index = 0
        right_index = self.menu_size

        # Building the context menu
        guide_string = "[key] to make (de)selection, [b] to go back"
        self.guidestring = guide_string
        recipe_names = [recipe['recipe_name'] for recipe in recipes]
        slot_map = self._update_option_slots(recipe_names, left_index, right_index)
        self.print_screen_context()

        def update_selected():
            """
                Changes font color of already-selected recipes to green
            """
            # Update already-selected recipes to green
            for key in slot_map:
                index = slot_map[key]
                if recipes[index]['selected']:
                    self.print_applycolor(key, 'green')

        update_selected()
        # Beginning input eval loop
        user_input: str = ""
        while user_input != 'b':
            self.screenbuf_input.FlushConsoleInputBuffer()  # Flushing input buffer just to be safe
            user_input = self._input_read()
            guide_string = "[key] to make (de)selection, [b] to go back"
            self.guidestring = guide_string
            if user_input in slot_map:  # A (de)selection was made
                # Determining if action is selecting or deselecting
                recipe_index = slot_map[user_input]
                target_recipe = recipes[recipe_index]
                if target_recipe['selected']:  # Deselecting
                    target_recipe['selected'] = 0
                    self.print_applycolor(user_input, 'gray')
                    self.callbacks['cb_recipe_deselect'](recipe_index)
                else:  # Selecting
                    target_recipe['selected'] = 1
                    self.print_applycolor(user_input, 'green')
                    self.callbacks['cb_recipe_select'](recipe_index)
            elif self._paged(  # user pressed k
                        recipe_names,
                        left_index,
                        right_index,
                        "right",
                        user_input):

                right_index += self.menu_size
                left_index += self.menu_size
                slot_map = self._update_option_slots(recipe_names, left_index, right_index)
                self.print_screen_context()
                update_selected()
            elif self._paged(recipe_names,  # user pressed j
                             left_index,
                             right_index,
                             "left",
                             user_input):
                left_index -= self.menu_size
                right_index -= self.menu_size
                slot_map = self._update_option_slots(recipe_names, left_index, right_index)
                self.print_screen_context()
                update_selected()

    def _paged(self
               , option_list: list
               , left_index: int
               , right_index: int
               , direction: str
               , user_input: str) -> bool:
        """
            Returns true if the user is able to page the menu in the stated direction

        :param direction:
        :return:  bool
        """

        if user_input == 'k' and direction == 'right':
            if right_index < len(option_list):
                return True

        elif user_input == 'j' and direction == 'left':
            if left_index > 0:
                return True

        return False

    def print_screen_context(self) -> None:
        """
            Prints the screen based on the contents of self.option_slots and self.guidestring
            In other words, the screen context.
        """
        clearline = self.ansi['clearline']
        for slot in self.option_slots:
            # Positioning cursor to begin writing
            option_slot = self.option_slots[slot]
            x_pos = option_slot['coords'][0]
            y_pos = option_slot['coords'][1]
            pycoord = win32console.PyCOORDType(x_pos, y_pos)
            self.screenbuf_output.SetConsoleCursorPosition(pycoord)
            # Writing text
            print(f'{clearline}', end="")
            if option_slot['text']:
                print(f"[{slot}]", option_slot['text'], end="")

        # Creating blank space between the bottom option and the input guide string
        x_pos = self.cursor_anchor[0]
        y_pos = self.cursor_anchor[1] + len(self.slot_titles) + 1  # +1 because the top line is left blank as well
        pycoord = win32console.PyCOORDType(x_pos, y_pos)
        self.screenbuf_output.SetConsoleCursorPosition(pycoord)
        print(f'{clearline}', end="")

        # Printing the input guide string
        pycoord = win32console.PyCOORDType(x_pos, y_pos + 1)
        self.screenbuf_output.SetConsoleCursorPosition(pycoord)
        print(f'{clearline}', self.guidestring, end="", sep="")

    def print_applycolor(self, slot_title: str, color: str) -> None:
        """

            Reprints the 'text' string of the given slot

            Our design up to this point didn't really account for how we want to coloring to be handled.
            As such, we are kind of bolting it on now.  Local menu context will need to make a call here,
            after calling print_screen_context, in order to applying any coloring.

            The presence of color is determined by the menu context method. It is NOT a stored value
            (at least not explicitly).
        """

        # Positioning cursor to the appropriate line
        x = self.option_slots[slot_title]['coords'][0]
        y = self.option_slots[slot_title]['coords'][1]
        pycoord = win32console.PyCOORDType(x, y)
        self.screenbuf_output.SetConsoleCursorPosition(pycoord)

        # Engaging color and reprinting string
        color_seq = self.ansi[color]  # Getting ANSI escape sequence corresponding to the desired color
        # Retrieving original text
        text = self.option_slots[slot_title]['text']
        # Preparing to disable color
        plain_seq = self.ansi['gray']
        # Finalizing
        print(f"{color_seq}[{slot_title}] {text}{plain_seq}")

    def _input_read(self):
        """
            I will probably need to add a filter here to ignore any non-key presses. Even then, I might have
            to filter out based on what counts as a KeyEvent e.g. key being released.
        """
        input_event = self.screenbuf_input.ReadConsoleInput(1)
        char = input_event[0].Char
        return char

    def mainloop(self):
        while True:
            self._mainmenu()
