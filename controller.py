import planner
import communicator
import json


class Controller:

    def __init__(self):
        self.recipes: list = self._read_recipes()
        self.planner = planner.Planner(self.recipes)
        self.customer_communicator = communicator.CustomerCommunicator()
        self.app_communicator = communicator.AppCommunicator()

    def _read_recipes(self):
        recipes: list[dict]
        with open('test_recipes.json', 'r') as recipe_file:
            recipes = json.load(recipe_file)

        return recipes

    def print_recipes(self, recipes):
        for recipe_index, recipe in enumerate(recipes):
            recipe_name = recipe['recipe_name']
            print(f'[{recipe_index}] {recipe_name}')

    def print_menu(self):
        print('[0]: Review recipes')
        print('[1]: Review selected recipes')
        print('[2]: Review shopping list')
        print('[3]: Build shopping list from selected recipes')
        print('[4]: Select recipe')
        print('[5]: Deselect recipe')
        print('[6]: Delete from shopping list')
        print('[7]: Confirm order')

    def get_input(self, message):
        selection = input(message)
        while True:
            try:
                int(selection)
                return selection
            except ValueError as ve:
                print('Invalid option..try again\n')

    def mainloop(self):
        while True:
            self.print_menu()
            selection = self.get_input('')
            # Review recipes
            if selection == '0':
                recipes = self.planner.recipes
                self.print_recipes(recipes)
                input('enter any key to continue...')
            # review selected recipes
            elif selection == '1':
                selected_recipes = self.planner.recipes_get_selected()
                self.print_recipes(selected_recipes)
                input('enter any key to continue...')
            # review shopping list
            elif selection == '2':
                shopping_order = self.planner.grocery_order
                for upc in shopping_order:
                    product = shopping_order[upc]['colloquial_name']
                    quantity = shopping_order[upc]['quantity']
                    print(f'[{upc}]: {product}, {quantity}')
                input('Hit any key to continue...')
            # build shopping list from selected recipes
            elif selection == '3':
                self.planner.grocery_buildfrom_selected()
                print('built grocery list from selected recipes')
            # select recipe
            elif selection == '4':
                recipes = self.planner.recipes
                self.print_recipes(recipes)
                selection = self.get_input('select a recipe [index]')
                try:
                    self.planner.recipes_select(int(selection))
                    print('Recipe added')
                except KeyError as ke:
                    print('Invalid selection...press any key to continue')
            # delete recipe
            elif selection == '5':
                # printing selected recipes
                selected_recipes = self.planner.recipes_get_selected()
                self.print_recipes(int(selected_recipes))
                # gathering human input
                selection = self.get_input('Make your selection:')
                try:
                    self.planner.recipes_deselect(int(selection))
                    print('Deselected the recipe')
                except KeyError as ke:
                    input('Invalid selection...enter any key to continue')
            # delete from shopping list
            elif selection == '6':
                shopping_order = self.planner.grocery_order
                for upc in shopping_order:
                    product = shopping_order[upc]['colloquial_name']
                    quantity = shopping_order[upc]['quantity']
                    print(f'[{upc}]: {product}, {quantity}')

                target_upc = self.get_input('Enter UPC of target product')
                target_quantity = self.get_input('What quantity are you removing?')

                try:
                    self.planner.grocery_subtractfrom(target_upc, int(target_quantity))
                    print('grocery list updated')
                except KeyError as ke:
                    input('Invalid upc...enter any key to continue')
            # Confirm and execute order
            elif selection == '7':
                self.execute_order()

    def execute_order(self):
        # Formatting order for API consumption
        grocery_order = self.planner.grocery_order
        cart_formatted = []
        for upc in grocery_order.keys():

            new_dict = {'upc': upc
                        , 'quantity': grocery_order[upc]['quantity']}
            cart_formatted.append(new_dict)

        print('gettting access token')
        self.customer_communicator.get_tokens()
        print('Adding items to cart')
        self.customer_communicator.add_to_cart(cart_formatted)
        print('Added to cart')









