"""
    @TODO: Need file-writing method
            New recipes will require updating the recipes.json file. Should create a swap and then verify
            the new file contains everything the old one did. Should probably create a FileIO class.

    @TODO: Move interface functionality to View.py
"""


# Project components
import planner
import communicator
import view
# Other modules
import json
import time


class Controller:

    def __init__(self):
        # Instantiating Planner (model)
        self.recipes: list = self.read_recipes()
        self.planner = planner.Planner(self.recipes)
        # Instantiating API interfaces
        self.customer_communicator = communicator.CustomerCommunicator()
        self.app_communicator = communicator.AppCommunicator()
        # Instantiating the view
        self.view = view.View()

        # Providing callback handles to self.view
        self.set_callbacks()

        # FOR DEBUGGINGG
        self.view._mainmenu()
        # self.view.mainloop()

    def read_recipes(self):
        recipes: list[dict]
        with open('test_recipes.json', 'r') as recipe_file:
            recipes = json.load(recipe_file)

        return recipes

    def set_callbacks(self):
        """
            Provides callback functions to the view for use in the "event loop"

        """
        self.view.callbacks['cb_recipes_get'] = self.get_recipes
        self.view.callbacks['cb_recipe_select'] = self.select_recipe
        self.view.callbacks['cb_recipe_deselect'] = self.deselect_recipe
        self.view.callbacks['cb_grocery_buidlist'] = self.build_grocery_list
        self.view.callbacks['cb_grocery_modifylist'] = self.modify_grocery_list

    def get_recipes(self):
        return self.planner.recipes

    def select_recipe(self, recipe_index):
        """
            Marks the given recipe as selected in the Planner
        :param recipe_index: index value of the recipe as found in Planner.recipes
        """
        self.planner.recipes_select(recipe_index)

    def deselect_recipe(self, recipe_index):
        """
            Marks the given recipe as unselected in the Planner
        :param recipe_index: index value of the recipe as found in Planner.recipes
        """
        self.planner.recipes_deselect(recipe_index)

    def build_grocery_list(self) -> dict:
        """
            Calls on Planner to construct the "grocery_order" dictionary based on the selected recipes.
            Then iterates through each entry and asks CustomerCommunicator to retrieve the price and size
            of each item. Grocery_order is updated accordingly before returning the dictionary to caller.

        :return: grocery_order: dict
        """

        # Summing recipe ingredients
        self.planner.grocery_buildfrom_selected()

        # Retrieving pricing information for each item
        for upc in self.planner.grocery_order.keys():
            # Asking server
            product_id = self.planner.grocery_order[upc]['product_id']
            product_info = self.customer_communicator.get_productinfo(product_id)
            time.sleep(1)  # Respecting rate limits
            # Price info
            regular_price = product_info['data']['items'][0]['price']['regular']
            promo_price = product_info['data']['items'][0]['price']['promo']
            price = promo_price if promo_price > 0 else regular_price
            # Size info
            size = product_info['data']['items'][0]['size']

            # Updating local values
            self.planner.grocery_order[upc]['price'] = price
            self.planner.grocery_order[upc]['size'] = size

        return self.planner.grocery_order

    def modify_grocery_list(self, upc: str, quantity: int) -> int:
        """
            Returns the quantity of the given item after "quantity" is added to it.
        """
        return self.planner.grocery_modifyquantity(upc, quantity)



    def mainloop(self):
        self.view._mainmenu()













    # def print_recipes(self, recipes):
    #     for recipe_index, recipe in enumerate(recipes):
    #         recipe_name = recipe['recipe_name']
    #         print(f'[{recipe_index}] {recipe_name}')
    #
    # def print_menu(self):
    #     print('[0]: Review recipes')
    #     print('[1]: Review selected recipes')
    #     print('[2]: Review shopping list')
    #     print('[3]: Build shopping list from selected recipes')
    #     print('[4]: Select recipe')
    #     print('[5]: Deselect recipe')
    #     print('[6]: Delete from shopping list')
    #     print('[7]: Confirm order')
    #
    # def get_input(self, message):
    #     selection = input(message)
    #     while True:
    #         try:
    #             int(selection)
    #             return selection
    #         except ValueError as ve:
    #             print('Invalid option..try again\n')
    #
    # def mainloop(self):
    #     while True:
    #         self.print_menu()
    #         selection = self.get_input('')
    #         # Review recipes
    #         if selection == '0':
    #             recipes = self.planner.recipes
    #             self.print_recipes(recipes)
    #             input('enter any key to continue...')
    #         # review selected recipes
    #         elif selection == '1':
    #             selected_recipes = self.planner.recipes_get_selected()
    #             self.print_recipes(selected_recipes)
    #             input('enter any key to continue...')
    #         # review shopping list
    #         elif selection == '2':
    #             shopping_order = self.planner.grocery_order
    #             for upc in shopping_order:
    #                 product = shopping_order[upc]['colloquial_name']
    #                 quantity = shopping_order[upc]['quantity']
    #                 print(f'[{upc}]: {product}, {quantity}')
    #             input('Hit any key to continue...')
    #         # build shopping list from selected recipes
    #         elif selection == '3':
    #             self.planner.grocery_buildfrom_selected()
    #             print('built grocery list from selected recipes')
    #         # select recipe
    #         elif selection == '4':
    #             recipes = self.planner.recipes
    #             self.print_recipes(recipes)
    #             selection = self.get_input('select a recipe [index]')
    #             try:
    #                 self.planner.recipes_select(int(selection))
    #                 print('Recipe added')
    #             except KeyError as ke:
    #                 print('Invalid selection...press any key to continue')
    #         # delete recipe
    #         elif selection == '5':
    #             # printing selected recipes
    #             selected_recipes = self.planner.recipes_get_selected()
    #             self.print_recipes(int(selected_recipes))
    #             # gathering human input
    #             selection = self.get_input('Make your selection:')
    #             try:
    #                 self.planner.recipes_deselect(int(selection))
    #                 print('Deselected the recipe')
    #             except KeyError as ke:
    #                 input('Invalid selection...enter any key to continue')
    #         # delete from shopping list
    #         elif selection == '6':
    #             shopping_order = self.planner.grocery_order
    #             for upc in shopping_order:
    #                 product = shopping_order[upc]['colloquial_name']
    #                 quantity = shopping_order[upc]['quantity']
    #                 print(f'[{upc}]: {product}, {quantity}')
    #
    #             target_upc = self.get_input('Enter UPC of target product')
    #             target_quantity = self.get_input('What quantity are you removing? Values are cast to int')
    #
    #             try:
    #                 self.planner.grocery_subtractfrom(target_upc, int(target_quantity))
    #                 print('grocery list updated')
    #             except KeyError as ke:
    #                 input('Invalid upc...enter any key to continue')
    #         # Confirm and execute order
    #         elif selection == '7':
    #             self.execute_order()
    #
    # def execute_order(self):
    #     # Formatting order for API consumption
    #     grocery_order = self.planner.grocery_order
    #     cart_formatted = []
    #     for upc in grocery_order.keys():
    #
    #         new_dict = {'upc': upc
    #                     , 'quantity': grocery_order[upc]['quantity']}
    #         cart_formatted.append(new_dict)
    #
    #     print('getting access token')
    #     self.customer_communicator.get_tokens()
    #     print('Adding items to cart')
    #     self.customer_communicator.add_to_cart(cart_formatted)
    #     print('Added to cart')









