
class Planner:

    def __init__(self, recipes: list[dict]):
        # Converting list of recipes to dictionary
        self.recipes: list[dict] = recipes
        for recipe in self.recipes:
            recipe['selected'] = 0

        self.grocery_order = dict()  # {upc:  {'colloquial_name': <>, 'quantity'}

    def recipes_get(self):
        return self.recipes

    def recipes_select(self, recipe_index):
        self.recipes[recipe_index]['selected'] = 1

    def recipes_deselect(self, recipe_index):
        self.recipes[recipe_index]['selected'] = 0

    def recipes_get_selected(self):
        return [recipe for recipe in self.recipes if recipe['selected'] == 1]

    def recipe_tallyitems(self, recipe: dict):
        """
            Returns {<upc>: {"colloquial_name": <>, {"quantity": <x>}, }
        :param recipe:
        :return:
        """
        items = dict()
        for item in recipe['recipe_items']:
            upc = item['upc']
            colloq_name = item['colloquial_name']
            quantity = float(item['quantity'])
            if upc in items.keys():
                items[upc]['quantity'] += quantity
            else:
                items[upc] = {'colloquial_name': colloq_name,
                              'quantity': quantity}

        return items

    def grocery_buildfrom_selected(self):
        """
            Populates self.grocery_order into {<upc>: {"colloquial_name": <>, "quantity": <>}, }
            structure.

            All item quantities are rounded up to the nearest integer value

            Resets self.grocery_order
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
                    self.grocery_order[upc] = {'colloquial_name': colloq_name,
                                               'quantity': quantity}

        # Rounding up and casting to int
        for upc in self.grocery_order.keys():
            original_quant = self.grocery_order[upc]['quantity']
            int_quant = int(self.grocery_order[upc]['quantity'])
            if original_quant != int_quant:  # Value is a float
                self.grocery_order[upc]['quantity'] = int(1 + original_quant)
            else:  # Casting to int to eliminate possible floats e.g. 3.0
                self.grocery_order[upc]['quantity'] = int_quant

    def grocery_subtractfrom(self, upc, quantity):
        try:
            self.grocery_order[upc]['quantity'] -= quantity
            if self.grocery_order[upc]['quantity'] <= 0:
                self.grocery_order.pop(upc)
        except KeyError as ke:
            print('no such items exists to delete..')
            raise KeyError

