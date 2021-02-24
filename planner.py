
class Planner:

    def __init__(self, recipes: list[dict]):
        # Converting list of recipes to dictionary
        self.recipes: list[dict] = recipes
        for recipe in self.recipes:
            recipe['selected'] = 0

        self.new_recipe: dict = None  # Temp var for when user is creating a new recipe
        # Grocery order - tally of ingredients/items for ordering
        self.grocery_order = dict()    # Formatted to allow API to consume items
        """
            {upc:  {'colloquial_name': <>, 
                    'product_id': <>,
                    'quantity': <>,
                    'price': <>, 
                    'upc': <>,  
                    'size': <e.g. 1 lb>}
                    
        """
        # Grocery_recipe contains many of the same structures as the grocery_order
        # But is in "recipe" format to allow the view to process it.
        self.grocery_recipe = dict()

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
                           , 'recipe_items': []
                           , 'selected':  0}
        return True

    def recipe_newrecipe_additem(self, item: dict) -> bool:
        """
            Requires the name given by the user to be unique. Return bool reflects this.

        :param item: {'colloquial_name': str(<name>)
                      , 'product_id': str(<id>)
                      , 'upc': str(<upc>)
                      , 'quantity': str(<quantity>) of a float
        """
        # I guess we are going to require colloquial_name to be unique so that modifyitem works as expected all the time
        for existing_recipe_item in self.new_recipe['recipe_items']:
            if existing_recipe_item['colloquial_name'] == item['colloquial_name']:
                return False

        # Name not already in use
        self.new_recipe['recipe_items'].append(item)
        return True

    def recipe_newrecipe_modifyitem(self, colloquial_name: str, quantity: float):
        """
            Changes the recipe item corresponding to the given colloquial_name to the given quantity.
            If the quantity is 0 or less the item is removed from the recipe.

        """
        for index, item in enumerate(self.new_recipe['recipe_items']):
            if item['colloquial_name'] == colloquial_name:
                item['quantity'] = quantity
                if item['quantity'] <= 0:
                    self.new_recipe['recipe_items'].pop(index)

    def recipe_newrecipe_save(self):
        """
            Saves the in-progress recipe to "recipe_list", which contains all of the recipes read from disk at
            boot as well as any other recipes created by the user in the current session.
        """

        self.recipes.append(self.new_recipe)
        self.new_recipe = None

    def recipe_tallyitems(self, recipe: dict):
        """
            Groups all like ingredients based on UPC.

            Returns {<upc>: {"colloquial_name": <>,
                             "quantity": <x>,
                             "product_id": <id> }
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

    def grocery_additem(self, new_item):
        """
        Add given item to the grocery "recipe"
        :param new_item:
                        {   "colloquial_name",
                            "product_id",
                            "upc",
                            "quantity",
                            "price",
                            "size",
                            "description"
                        }
        """
        for ingredient in self.grocery_recipe['recipe_items']:
            if ingredient['upc'] == new_item['upc']:
                ingredient['quantity'] += new_item['quantity']
                return

        self.grocery_recipe['recipe_items'].append(new_item)

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

    def grocery_buildfrom_selected(self):
        """
            Overwrites self.grocery_order based on ingredients of the selected recipes

            All item quantities are rounded up to the nearest integer value
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
                                               'upc': upc,
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
