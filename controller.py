"""
"""


# Project components
import planner
import communicator
import view
# Other modules
import json
import time
import os
import copy


class Controller:

    def __init__(self, disableview=False, get_tokens=True):
        # Instantiating Planner (model)
        self.recipes: list = self.read_recipes()
        self.planner = planner.Planner(self.recipes)
        # Instantiating API interfaces
        self.customer_communicator = communicator.CustomerCommunicator()
        self.app_communicator = communicator.AppCommunicator()

        if get_tokens:
            print("Please wait while we retrieve the tokens..")
            self.customer_communicator.get_tokens()
            print("Tokens received")

        if not disableview:  # To facilitate testing
            # Instantiating the view
            self.view = view.View()

            # Providing callback handles to self.view
            self.set_callbacks()
            self.mainloop()

    def read_recipes(self):
        recipes: list[dict]
        with open('test_recipes.json', 'r') as recipe_file:
            recipes = json.load(recipe_file)
            recipes.sort(key=lambda recipe: recipe['recipe_name'])

        return recipes

    def set_callbacks(self):
        """
            Provides callback functions to the view for use in the "event loop"

        """
        # Recipe Callbacks
        self.view.callbacks['cb_recipes_get'] = self.get_recipes
        self.view.callbacks['cb_recipe_select'] = self.select_recipe
        self.view.callbacks['cb_recipe_deselect'] = self.deselect_recipe
        self.view.callbacks['cb_recipe_newrecipe'] = self.recipe_newrecipe
        self.view.callbacks['cb_recipe_newrecipe_additem'] = self.recipe_newrecipe_additem
        self.view.callbacks['cb_recipe_newrecipe_modifyitem'] = self.recipe_newrecipe_modifyitem
        self.view.callbacks['cb_recipe_newrecipe_save'] = self.recipe_newrecipe_save

        # Grocery list callbacks
        self.view.callbacks['cb_grocery_buidlist'] = self.build_grocery_list
        self.view.callbacks['cb_grocery_modifylist'] = self.modify_grocery_list

        self.view.callbacks['cb_product_search'] = self.product_search

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

    def recipe_newrecipe(self, recipe_name: str) -> bool:
        return self.planner.recipe_new_recipe(recipe_name)

    def product_search(self, search_string: str, page_size: int, direction: str = "") -> list[dict]:
        """
            Caller must make sure the search_string is at least 3 characters in length.
            That is the requirement of the kroger API

            "direction" instructs the communicator object to "paginate" the results of the API call.
            It remembers the previous position in the results page.

            We will format the information for the view.
        """
        assert(len(search_string) >= 3)
        req_results = self.customer_communicator.product_search(search_string, page_size, direction)
        search_results = req_results['data']

        desired_results = []
        for result in search_results:
            try:
                product_dict = dict()
                product_dict['description'] = result['description']
                product_dict['product_id'] = result['productId']
                product_dict['size'] = result['items'][0]['size']
                product_dict['price'] = result['items'][0]['price']
                product_dict['upc'] = result['upc']
                desired_results.append(product_dict)
            except KeyError:
                continue

        return desired_results

    def recipe_newrecipe_additem(self, item: dict) -> bool:
        return self.planner.recipe_newrecipe_additem(item)

    def recipe_newrecipe_modifyitem(self, colloquial_name: str, quantity: float):
        self.planner.recipe_newrecipe_modifyitem(colloquial_name, quantity)

    def recipe_newrecipe_save(self) -> bool:
        """
            Controller here attempts to save the recipe to disk after instructing Planner to comingle the new recipe
            with the established recipes.
        :return: Indicate success of Controller to write the new recipe to disk and verify the contents of the recipe
        file

        """
        # Preparing for disk write
        self.planner.recipe_newrecipe_save()
        recipe_list = copy.deepcopy(self.planner.recipes)

        # Need to remove the "selected" field
        for recipe in recipe_list:
            del(recipe['selected'])

        # Writing to disk
        with open("updated_recipes.json", "w+") as updated_recipe_file:
            json.dump(recipe_list, updated_recipe_file, indent=4)

        # Reading back info to check for completeness
        with open("updated_recipes.json", "r") as read_file:
            read_recipes = json.load(read_file)
            # informing caller of failure should it be so
            if read_recipes != recipe_list:
                return False

        # All recipes written to disk. Moving tmp file to overwrite perennial
        os.replace("updated_recipes.json", "recipes.json")
        return True

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
        self.view.mainloop()





