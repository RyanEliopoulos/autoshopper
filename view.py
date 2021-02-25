"""
    It seems the cursor might be getting toggled to become visible again after being made invisible in the init fnx.

    @TODO Offer a graceful way of shutting down. Console settings aren't reverted by the program and there is a
            "quit" button.
"""
import win32console  # Module for calling the win32 api
from colorama import init as colorinit  # Enables ANSI escape sequence for terminals


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
            , 'cb_recipe_rename': None
            , 'cb_recipe_additem': None

            , 'cb_product_search': None

            , 'cb_grocery_buildlist': None
            , ' cb_grocery_moodifylist': None

            , 'cb_fill_cart': None
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

    def input_mirror_enable(self):
        """
            Toggle mode of the console echo. Based on the win32 API requirements
            https://docs.microsoft.com/en-us/windows/console/setconsolemode
        """
        self.screenbuf_input.SetConsoleMode(self.screenbuf_input_default)

    def input_mirror_disable(self):
        """
            Turns off input echo.  Input buffer now updates without need for a newline character.
        """
        self.screenbuf_input.SetConsoleMode(0)

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

    def _input_read(self):
        """
            Reads events reported by the screen input buffer.  Filters out all events
            that are not a KeyEvent in the KeyDown state
        """

        # Will not return until a KEY_EVENT is detected. All others are ignored.
        input_event = self.screenbuf_input.ReadConsoleInput(1)
        while True:
            if input_event[0].EventType == win32console.KEY_EVENT:
                if input_event[0].KeyDown:
                    break
            input_event = self.screenbuf_input.ReadConsoleInput(1)
        char = input_event[0].Char
        return char

    def clear_screen(self):
        """
            Taking advantage of some shortcut possible with the update call to clear the lines
            of the context menu
        """
        self._update_option_slots([], 0, 0)
        self.print_screen_context()

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

    def _update_option_slots(self
                             , options: list[str]
                             , left_index: int
                             , right_index: int) -> dict:

        """
            Slices the given options list based on the passed indices. Then maps them to self.option_slots
            as well as providing a dictionary mapping {<slot_title>: <index>} to caller so that they may
            reference selected item in its scope.

            It is up to caller to bounds check the indices.

            Also updates the guidestring based on the indices

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

    def mainloop(self):
        while True:
            self._mainmenu()

    def _mainmenu(self):
        # Building context menu
        options = ['Select Recipes',
                   'Build Recipe',
                   'Finalize Grocery List',
                   'Fill Cart']
        # Reversing because the "first" option is the one nearest the bottom
        # and I want Select Recipes at the top
        options.reverse()

        # Establishing guide string
        # This is a string present in every menu
        # offer explanation on functionality
        guidestring = "[key] to make a selection"
        self.guidestring = guidestring

        # The difference here represents the number of menu items displayed per context
        left_index = 0
        right_index = self.menu_size

        # We don't need to use the returned dictionary because we
        # Don't care about the list entries
        self._update_option_slots(options, left_index, right_index)
        self.print_screen_context()

        # These correspond to menu options. I thought I would be clever
        # and call them from the dictionary but it is difficult to read
        actions = {
            'g': self._fill_cart,
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

    def _recipes_select(self):
        """
            This is the screen where users page through their recipes. Selection mode marks recipes (really their
            ingredients) for later tallying into a final shopping list.  Edit mode allows the recipes to be updated.

        """

        # Retrieving recipes from the planner
        recipes = self.callbacks['cb_recipes_get']()
        # Establishing recipe navigation variables
        left_index = 0
        right_index = self.menu_size

        # Building the context menu
        edit_mode = False
        guide_string = ":Selection Mode: [b] to go back, [e] edit mode"
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

            if edit_mode:
                guide_string = ':Edit Mode: [b] back, [e] selection mode'
            else:
                guide_string = ':Selection Mode: [b] back, [e] edit mode'

            if user_input == 'e':
                # Changing modes
                edit_mode = not edit_mode
                if edit_mode:
                    guide_string = ':Edit Mode: [b] back, [e] selection mode'
                else:
                    guide_string = ':Selection Mode: [b] back, [e] selection mode'
                # Checking pagination
                if left_index > 0:
                    guide_string += ', [j] page left'
                if right_index < len(recipe_names):
                    guide_string += ', [k] page right'
                self.guidestring = guide_string
                self.print_screen_context()
                update_selected()

            # Selecting ingredient
            elif user_input in slot_map:  # A selection was made
                # Checking mode
                if edit_mode:
                    # Saving guide string for next loop
                    guide_string = self.guidestring
                    # Updating a recipe
                    recipe_index = slot_map[user_input]
                    recipe = recipes[recipe_index]
                    self._menu_modifyrecipe('existing', recipe_index, recipe)
                    # Updating view with latest recipe info
                    recipes = self.callbacks['cb_recipes_get']()
                    recipe_names = [recipe['recipe_name'] for recipe in recipes]
                    # Rebuilding menu
                    slot_map = self._update_option_slots(recipe_names, left_index, right_index)
                    # refreshing guide string
                    self.guidestring = guide_string
                    self.print_screen_context()
                    update_selected()

                else:
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
                    'right',
                    user_input):

                right_index += self.menu_size
                left_index += self.menu_size
                self.guidestring = guide_string
                slot_map = self._update_option_slots(recipe_names, left_index, right_index)
                self.print_screen_context()
                update_selected()
            elif self._paged(recipe_names,  # user pressed j
                             left_index,
                             right_index,
                             'left',
                             user_input):
                left_index -= self.menu_size
                right_index -= self.menu_size
                self.guidestring = guide_string
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
            Returns true if the user is able to page the menu in the stated direction based on the current value of
            the indices and user_input. "k" is always page right and "j" is always page left.

        :return:  bool
        """

        if user_input == 'k' and direction == 'right':
            if right_index < len(option_list):
                return True

        elif user_input == 'j' and direction == 'left':
            if left_index > 0:
                return True

        return False

    def _menu_buildrecipe(self):
        """
            Building a recipe from scratch
            Should have two options:
                                    Edit Recipe
                                    Save recipe
        :return:
        """
        # Clearing screen
        self._update_option_slots([], 0, 0)
        self.guidestring = "Enter the name of the recipe: "
        self.print_screen_context()

        # Receiving recipe name
        self.input_mirror_enable()
        recipe_name = input("")

        # Checking if name already in use
        if not self.callbacks['cb_recipe_newrecipe'](recipe_name):
            self.guidestring = "That name is already used. Press enter to continue"
            self.print_screen_context()
            input("")
            return
        # Building menu
        options = ['Edit recipe', 'Save recipe']
        options.reverse()
        left_index = 0
        right_index = self.menu_size

        new_recipe = self.callbacks['cb_newrecipe_struct']()
        # Beginning eval loop
        user_input: str = ''
        while user_input != 'b':
            recipe_name = new_recipe['recipe_name']
            # printing screen
            self.screenbuf_input.FlushConsoleInputBuffer()
            self.guidestring = f'Building "{recipe_name}".  [b] for back'
            self._update_option_slots(options, left_index, right_index)
            self.input_mirror_disable()
            self.print_screen_context()

            user_input = self._input_read()
            if user_input == 'g':
                if len(new_recipe['recipe_items']) == 0:
                    self.guidestring = "Cannot save an empty recipe. Enter to continue"
                    self.print_screen_context()
                    self.input_mirror_enable()
                    input("")
                    self.input_mirror_disable()
                else:
                    self._recipe_newrecipe_save()
                return
            elif user_input == 'f':
                self._menu_modifyrecipe('new', 99999, new_recipe)

    def _menu_recipe_additem(self, target: str, recipe_index: int):
        """
            Asks user for a search term that is then used to search the API
            The menu context then populates with the values. Users can page through
            more results, if possible, which results in querying the API. It's possible for users
            to continue paging into blank results, as provided by the API.
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
            if len(search_string) < 3:  # API requires at least this many chars
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
                # "try" because current mechanism queries the API directly
                self.guidestring = "[r] retry, [b] return, [j] and [k] to paginate"
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
                        quantity = float(quantity)
                        # Adding item to planner and return to the previous menu
                        new_item = {
                            'colloquial_name': colloquial_name
                            , 'description': selection['description']
                            , 'product_id': selection['product_id']
                            , 'upc': selection['upc']
                            , 'quantity': quantity
                            , 'price': selection['price']
                            , 'size': selection['size']
                        }
                        if target == 'new':
                            self.callbacks['cb_recipe_newrecipe_additem'](new_item)
                            return
                        elif target == 'existing':
                            self.callbacks['cb_recipe_additem'](target, recipe_index, new_item)
                        elif target == 'grocery':
                            self.callbacks['cb_recipe_additem'](target, recipe_index, new_item)

                    except ValueError:
                        # User entered a non-number character. Ignoring
                        continue

    def _menu_modifyrecipe(self
                           , target: str
                           , recipe_index: int
                           , recipe: dict) -> None:
        """
            Will be used:
                1) from the "Select Recipe" screen to modify existing recipes
                2) From the "Build Recipe" screen to modify selected items
                3) from the "Build Grocery List" screen to make changes to the grocery list.
                    We conceive the grocery list to be a special instance of a recipe.

        Target: existing, new, or grocery. New means modify the new recipe, existing means it's modifying
                a recipe that is in the planner's recipe list already, and grocery means that it is modifying
                the special "recipe" that tracks the grocery list.
        """

        # Slice indices
        left_index = 0
        right_index = self.menu_size

        # Input eval loop
        user_input: str = ""
        while user_input != 'b':
            # Building screen
            recipe_name = recipe['recipe_name']
            self._update_option_slots([], 0, 0)  # Clearing screen
            self.guidestring = f"Editing {recipe_name}: Select item to modify. [n] Renames recipe. [m] adds ingredient"
            options = recipe['recipe_items']
            slot_map = self._update_option_slots(options, left_index, right_index)
            self.print_screen_context()
            self.screenbuf_input.FlushConsoleInputBuffer()

            # Reading input
            user_input = self._input_read()

            # Interpreting input
            if user_input == 'n':
                self.guidestring = "What do you wish to name it?"
                self.clear_screen()
                self.input_mirror_enable()
                new_name = input("")
                self.callbacks['cb_recipe_rename'](target, recipe_index, new_name)
                self.input_mirror_disable()
            elif user_input in slot_map:
                # User chose to modify an ingredient
                ingredient_index = slot_map[user_input]
                ingredient = recipe['recipe_items'][ingredient_index]
                self._menu_modify_ingredient(target, recipe_index, ingredient, ingredient_index)
            elif user_input == 'm':
                # Adding ingredient from API query
                self._menu_recipe_additem(target, recipe_index)

    def _menu_modify_ingredient(self, target: str, recipe_index: int, ingredient: dict, ingredient_index: int):
        """
            Allows caller to modify the "colloquial" name and quantity of the specified ingredient.

        :param target: "existing", "new", "grocery"
        :param recipe_index:
        """
        self.clear_screen()
        user_input: str = ''
        while user_input != 'b':
            self.guidestring = '[n] rename, [q] update quantity'
            self._update_option_slots([str(ingredient)], 0, self.menu_size)
            self.print_screen_context()
            user_input = self._input_read()

            # Processing input
            if user_input == 'n':
                self.guidestring = 'New name:'
                self.input_mirror_enable()
                self.print_screen_context()
                self.screenbuf_input.FlushConsoleInputBuffer()
                new_name = input("")
                self.callbacks['cb_ingredient_rename'](target, recipe_index, ingredient_index, new_name)
                ingredient['colloquial_name'] = new_name
                self.input_mirror_disable()
            elif user_input == 'q':
                self.guidestring = 'New quantity:'
                self.input_mirror_enable()
                self.print_screen_context()
                self.screenbuf_input.FlushConsoleInputBuffer()
                new_quantity = input("")
                try:
                    new_quantity = float(new_quantity)
                    self.callbacks['cb_ingredient_requant'](target, recipe_index, ingredient_index, new_quantity)
                    ingredient['quantity'] = new_quantity
                    if new_quantity == 0:
                        self.guidestring = "Item deleted. Press enter to continue"
                        self.print_screen_context()
                        self.input_mirror_enable()
                        input("")
                        self.input_mirror_disable()
                        return
                except ValueError:
                    # User entered a non-number char. Ignoring.
                    pass
                self.input_mirror_disable()

    def _build_cost_string(self, product_dict: dict) -> str:
        """
            Returns a single string with description + size + price formatted as specified in this method.

            accepts: {
                'description': <>
                , 'product_id': <>
                , 'size': <>
                , 'price': <>
                , 'upc': <>
            }
        """
        description = product_dict['description'][:50]
        size = product_dict['size']
        price = product_dict['price']

        return f"{description} @@ {price} PER {size}"

    def _recipe_newrecipe_save(self):
        """
            Communicates to the Controller -> Planner to save the in-memory recipe to disk.
        """
        if self.callbacks['cb_recipe_newrecipe_save']():
            # Save successful
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
        """
            User can overwrite the existing list, should it exist, with one derived solely from
            the recipes presently selected.

            The user may also choose to edit an existing list if such a list was already generated
        """
        grocery_recipe = self.callbacks['cb_grocery_get']()

        user_input: str = ''
        while user_input != 'b':
            # Building menu
            self.clear_screen()
            self.guidestring = '[q] Build list from selected recipes'
            if len(grocery_recipe) > 0:
                self.guidestring += ', [e] Edit existing grocery list'
            self.print_screen_context()
            self.screenbuf_input.FlushConsoleInputBuffer()
            user_input = self._input_read()

            # Parsing input
            if user_input == 'q':
                # (re)building grocery list
                grocery_recipe = self.callbacks['cb_grocery_buildlist']()
            elif user_input == 'e' and len(grocery_recipe) > 0:
                # grocery order is being treated like a special recipe
                self._menu_modifyrecipe('grocery', 99999, grocery_recipe)
                return

    def _fill_cart(self):
        """
            This will just call controller and have it load up all the
            items into the cart. This will result in an alpha version for the program
            whereby the core functionality is present. WIll just have to log in
            to finalize the details of the order.

        """
        # Filling cart
        self.clear_screen()
        self.guidestring = "Filling cart with order"
        self.print_screen_context()
        self.callbacks['cb_fill_cart']()

        # Cart filled. Informing user and returning
        self.guidestring = "Filling complete. Press enter to continue"
        self.print_screen_context()
        self.input_mirror_enable()
        input("")
        self.input_mirror_disable()

