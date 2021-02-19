
class Planner:

    def __init__(self, recipes: list[dict]):
        # Converting list of recipes to dictionary
        self.recipes: list[dict] = recipes
        for recipe in self.recipes:
            recipe['selected'] = 0

        self.new_recipe: dict = None  # Temp var for when user is creating a new recipe
        # Grocery order - tally of ingredients/items for ordering
        self.grocery_order = dict()
        """
            {upc:  {'colloquial_name': <>, 
                    'product_id': <>,
                    'quantity': <>,
                    'price': <>, 
                    'size': <e.g. 1 lb>}
        """

    def recipes_get(self):
        return self.recipes

    def recipes_select(self, recipe_index):
        self.recipes[recipe_index]['selected'] = 1

    def recipes_deselect(self, recipe_index):
        self.recipes[recipe_index]['selected'] = 0

    def recipes_get_selected(self):
        return [recipe for recipe in self.recipes if recipe['selected'] == 1]

    def recipe_new_recipe(self, recipe_name) -> bool:
        """
        :return: bool value. False  means the recipe name is  already in use. True means good to go.
        """
        # Checking that the recipe name is not already in use
        for recipe in self.recipes:
            if recipe['recipe_name'] == recipe_name:
                return False
        self.new_recipe = {'recipe_name': recipe_name
                           , 'recipe_items': []}
        return True

    def recipe_newrecipe_additem(self, item: dict):
        """
        :param item: {'colloquial_name': str(<name>)
                      , 'product_id': str(<id>)
                      , 'upc': str(<upc>)
                      , 'quantity': str(<quantity>) of a float
        """
        self.new_recipe['recipe_items'].append(item)

    def recipe_newrecipe_removeitem(self, colloquial_name):
        """
            This should be changed to modifyquantity. If the user wishes to remove the item from the recipe
            they can reduce the quantity of the item to 0.

        :param colloquial_name:
        :return:
        """
        for index, item in enumerate(self.new_recipe['recipe_items']):
            if item['colloquial_name'] == colloquial_name:
                self.new_recipe['recipe_items'].pop(index)

    def recipe_newrecipe_save(self):
        """
            Saves the in-progress recipe to the recipe list
        """
        self.recipes.append(self.new_recipe)
        self.new_recipe = None

    def recipe_tallyitems(self, recipe: dict):
        """
            Returns {<upc>: {"colloquial_name": <>,
                             "quantity": <x>,
                             "product_id": <id> }
        :param recipe:
        :return:
        """
        items = dict()
        for item in recipe['recipe_items']:
            upc = item['upc']
            colloq_name = item['colloquial_name']
            quantity = float(item['quantity'])
            product_id = item['product_id']
            if upc in items.keys():
                items[upc]['quantity'] += quantity
            else:
                items[upc] = {'colloquial_name': colloq_name,
                              'quantity': quantity,
                              'product_id': product_id}

        return items

    def grocery_buildfrom_selected(self):
        """
            Overwrites self.grocery_order based on ingredients of the selected recipes

            All item quantities are rounded up to the nearest integer value
        :return:  None
        """
        self.grocery_order = dict()

        # Constructing
        for recipe in self.recipes_get_selected():
            # Pulling recipe ingredients
            items = self.recipe_tallyitems(recipe)
            for upc in items.keys():
                # Adding recipe ingredients to grocery order
                if upc in self.grocery_order.keys():
                    self.grocery_order[upc]['quantity'] += items[upc]['quantity']
                else:
                    colloq_name = items[upc]['colloquial_name']
                    quantity = items[upc]['quantity']
                    product_id = items[upc]['product_id']
                    self.grocery_order[upc] = {'colloquial_name': colloq_name,
                                               'product_id': product_id,
                                               'quantity': quantity,
                                               'price': '?',
                                               'size': '?'}

        # Adding 1 to each quantity and casting to int, which rounds to floor
        for upc in self.grocery_order.keys():
            original_quant = self.grocery_order[upc]['quantity']
            int_quant = int(self.grocery_order[upc]['quantity'])
            if original_quant != int_quant:  # Value is a float
                self.grocery_order[upc]['quantity'] = int(1 + original_quant)
            else:  # Casting to int to eliminate possible floats e.g. 3.0
                self.grocery_order[upc]['quantity'] = int_quant

    def grocery_modifyquantity(self, upc: str, quantity: int) -> int:
        """
            Adds "quantity" to the existing self.grocery_order[upc] value
            Pops the UPC from the dictionary if the total quantity <= 0

            Raises KeyError if attempting to modify an UPC that isn't

            Returns the remaining quantity for the given item
        """
        try:
            self.grocery_order[upc]['quantity'] += quantity
            if self.grocery_order[upc]['quantity'] <= 0:
                self.grocery_order.pop(upc)
                return 0
            return self.grocery_order[upc]['quantity']

        except KeyError as ke:
            print('no such items exists to delete..')
            raise KeyError

