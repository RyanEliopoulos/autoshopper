"""
    @TODO It could be really cool to add multithreading to pre-fetch the product information from the server while
            the user is navigating the menus and making selection decisions instead of causing the program to pause
            when doing so.
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

    def __init__(self, disableview=False, stage_tokens=True):
        # Instantiating Planner (model)
        self.recipes: list = self.read_recipes()
        self.planner = planner.Planner(self.recipes)
        # Instantiating API interfaces
        self.customer_communicator = communicator.CustomerCommunicator()
        self.app_communicator = communicator.AppCommunicator()

        if stage_tokens:
            self.customer_communicator.stage_tokens()

        if not disableview:  # To facilitate testing
            # Instantiating the view
            self.view = view.View()
            # Providing callback handles to self.view
            self.set_callbacks()
            self.mainloop()

    def read_recipes(self):
        recipes: list[dict]
        with open('recipes.json', 'r') as recipe_file:
            recipes = json.load(recipe_file)
            # Alphabetizing
            recipes.sort(key=lambda recipe: recipe['recipe_name'].lower())

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
        self.view.callbacks['cb_newrecipe_struct'] = self.newrecipe_struct
        self.view.callbacks['cb_recipe_newrecipe_additem'] = self.recipe_newrecipe_additem
        self.view.callbacks['cb_recipe_newrecipe_modifyitem'] = self.recipe_newrecipe_modifyitem
        self.view.callbacks['cb_recipe_newrecipe_save'] = self.recipe_newrecipe_save
        self.view.callbacks['cb_recipe_rename'] = self.recipe_rename
        self.view.callbacks['cb_recipe_additem'] = self.recipe_additem

        # Ingredient callbacks
        self.view.callbacks['cb_ingredient_rename'] = self.ingredient_rename
        self.view.callbacks['cb_ingredient_requant'] = self.ingredient_requant

        # Grocery list callbacks
        self.view.callbacks['cb_grocery_buildlist'] = self.build_grocery_list
        self.view.callbacks['cb_grocery_modifylist'] = self.modify_grocery_list
        self.view.callbacks['cb_grocery_get'] = self.grocery_get

        # Other
        self.view.callbacks['cb_product_search'] = self.product_search
        self.view.callbacks['cb_fill_cart'] = self.fill_cart

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

    def newrecipe_struct(self):
        return self.planner.new_recipe

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

        # Alphabetizing recipe list again
        self.planner.recipes.sort(key=lambda recipe: recipe['recipe_name'].lower())
        return self.save_recipes()

    def recipe_additem(self, target: str, recipe_index: int, new_item: dict):
        """

        :param target: "existing", "new", or "grocery"

        :param new_item: The dictionary of the recipe_item. We will expect new the new_item to contain pricing
                        information that is to be stored, at least in memory.
        """

        if target == 'new':
            self.planner.recipe_newrecipe_additem(new_item)
        elif target == 'existing':
            self.planner.recipes[recipe_index]['recipe_items'].append(new_item)
        elif target == 'grocery':
            self.planner.grocery_additem(new_item)

    def recipe_rename(self, target: str, recipe_index: int, new_name: str):
        if target == "new":
            self.planner.new_recipe['recipe_name'] = new_name
        elif target == 'existing':
            self.planner.recipes[recipe_index]['recipe_name'] = new_name
            if not self.save_recipes():
                print("Couldn't save recipe to disk")
        elif target == "grocery":
            # Does nothing
            return

    def ingredient_rename(self, target: str, recipe_index: int, ingredient_index: int, new_name: str):
        if target == 'new':
            self.planner.new_recipe['recipe_items'][ingredient_index]['colloquial_name'] = new_name
        elif target == 'existing':
            self.planner.recipes[recipe_index]['recipe_items'][ingredient_index]['colloquial_name'] = new_name
            self.save_recipes()

        elif target == 'grocery':
            return

    def ingredient_requant(self, target, recipe_index: int, ingredient_index: int, new_quantity: int):
        """
            Updates the quantity value of the specified ingredient belonging to the specified recipe
        """
        if target == 'new':
            self.planner.new_recipe['recipe_items'][ingredient_index]['quantity'] = new_quantity
        elif target == 'existing':
            self.planner.recipes[recipe_index]['recipe_items'][ingredient_index]['quantity'] = new_quantity
            self.save_recipes()
        elif target == 'grocery':
            if new_quantity <= 0:
                self.planner.grocery_recipe['recipe_items'].pop(ingredient_index)
            else:
                self.planner.grocery_recipe['recipe_items'][ingredient_index]['quantity'] = new_quantity

    def save_recipes(self):
        """
            Saves recipes to disk
        """
        recipe_list = copy.deepcopy(self.planner.recipes)
        # Need to remove the "selected" field
        for recipe in recipe_list:
            del (recipe['selected'])

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

    def product_search(self, search_string: str, page_size: int, direction: str = "") -> list[dict]:
        """
            Caller must make sure the search_string is at least 3 characters in length.
            That is the requirement of the kroger API

            "direction" instructs the communicator object to "paginate" the results of the API call.
            It remembers the previous position in the results page.

            We will format the information for the view.
        """
        assert (len(search_string) >= 3)
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
                # Some items aren't formatted to the API spec
                # causing KeyErrors
                continue

        return desired_results

    def build_grocery_list(self) -> dict:
        """
            Orders Planner to construct a dictionary of { upc: {item info}}

            This method then retrieves pricing, size, and description information from the API for each item.
            Once the info is gathered this method translates the values into a special "recipe" that allows
            the view to manipulate the grocery list reusing the same methods.

        :return: grocery_order: dict
        """

        # Summing recipe ingredients
        self.planner.grocery_buildfrom_selected()
        grocery_dict = self.planner.grocery_order
        self.grocery_retrievepricing(grocery_dict)

        # Building grocery "recipe" for use by the view.
        # (passing references to the dictionaries)
        grocery_recipe = {
            'recipe_name': 'grocery_list'
            , 'recipe_items': []
        }

        for upc in grocery_dict:
            ingredient = grocery_dict[upc]
            grocery_recipe['recipe_items'].append(ingredient)
        self.planner.grocery_recipe = grocery_recipe

        return grocery_recipe

    def grocery_retrievepricing(self, grocery_dict):

        """
            Updates the grocery "recipe" with the latest price, size, and description information by querying
            the API.
        """
        # Retrieving pricing information for each item
        for upc in grocery_dict:
            if grocery_dict[upc]['price'] == '?':
                # Updating pricing info only if it wasn't present already
                # Asking server
                product_id = grocery_dict[upc]['product_id']
                product_info = self.customer_communicator.get_productinfo(product_id)
                time.sleep(1)  # Respecting rate limits
                # Price info
                description = product_info['data']['description']
                regular_price = product_info['data']['items'][0]['price']['regular']
                promo_price = product_info['data']['items'][0]['price']['promo']
                price = promo_price if promo_price > 0 else regular_price
                # Size info
                size = product_info['data']['items'][0]['size']

                # Updating local values
                grocery_dict[upc]['price'] = price
                grocery_dict[upc]['size'] = size
                grocery_dict[upc]['description'] = description

    def modify_grocery_list(self, upc: str, quantity: int) -> int:
        """
            Returns the quantity of the given item after "quantity" is added to it.
        """
        return self.planner.grocery_modifyquantity(upc, quantity)

    def grocery_get(self):
        return self.planner.grocery_recipe

    def fill_cart(self):
        """
            Loads up the digital shopping cart with the goods specified in the grocery "recipe"
        """
        # Formatting items as required by the API
        shopping_list = []
        for ingredient in self.planner.grocery_recipe['recipe_items']:
            trimmed_ingredient = {
                'upc': ingredient['upc']
                , 'quantity': ingredient['quantity']
            }
            shopping_list.append(trimmed_ingredient)
        self.customer_communicator.add_to_cart(shopping_list)

    def mainloop(self):
        self.view.mainloop()





