import DBInterface
import Logger
import copy


class Model:

    def __init__(self, db_interface: DBInterface):
        self.db_interface: db_interface = db_interface
        self.recipes: dict = self._get_recipes()
        self.selected_recipes: dict = {}

    def _valid_upc(self, kroger_upc: str) -> tuple[int, dict]:
        """
        Must be an empty string or a 13 digit string.
        Could just use regex here.
        :param kroger_upc:
        :return:
        """
        if kroger_upc == '':
            return 0, {}

        if type(kroger_upc) != str:
            return -1, {'error_message': f'kroger_upc must be type str not {type(kroger_upc)}'}
        try:
            cast_val: int = int(kroger_upc)
        except ValueError as ve:
            return -1, {'error_message': f'kroger_upc must include digits only: {ve}'}
        if len(kroger_upc) != 13:
            return -1, {'error_message': f'upc must be 13 digits long, not {len(kroger_upc)}'}

        return 0, {'success_message': 'valid_upc'}

    def _get_recipes(self) -> dict:
        """
        Initialization fnx. Loads recipe data into the Model.
        """
        ret = self.db_interface.get_recipes()
        if ret[0] != 0:
            Logger.Logger.log_error(f'Error in model._get_recipes pulling recipes -- ' + ret[1]['error_message'])
            print('Error in ._get_recipes -- ' + ret[1]['error_message'])
            exit(1)
        return ret[1]

    def add_recipe(self, recipe: dict) -> tuple[int, dict]:
        """
        Returns recipe with recipe_id and ingredient_ids added.
        Updates database and Model.
        Should use new_recipe instead to build the recipe
        one component at at time
        """
        ret = self.db_interface.add_recipe(recipe)
        if ret[0] != 0:
            return ret
        new_recipe: dict = ret[1]
        recipe_id: int = new_recipe['recipe_id']
        self.recipes[recipe_id] = new_recipe
        view_copy: dict = copy.deepcopy(new_recipe)
        return 0, view_copy

    def new_recipe(self) -> tuple[int, dict]:
        """
        Instantiates a new, blank recipe in the database and model
        """
        ret = self.db_interface.new_recipe()
        if ret[0] == 0:
            new_recipe: dict = {
                'recipe_title': '',
                'recipe_notes': '',
                'ingredients': {}
            }
            recipe_id: int = ret[1]['recipe_id']
            new_recipe['recipe_id'] = recipe_id
            self.recipes[recipe_id] = new_recipe
        return ret

    def delete_recipe(self, recipe_id: int) -> tuple[int, dict]:
        """
        Updates database and Model.
        :param recipe_id:
        :return:
        """
        ret = self.db_interface.delete_recipe(recipe_id)
        if ret[0] == 0:
            self.recipes.pop(recipe_id)
            self.selected_recipes.pop(recipe_id, 'NULL')
        return ret

    def toggle_recipe(self, recipe_id: int) -> None:
        """
        Selects or deselects the given recipe, toggling
        its selection for automatic shopping.
        """
        if recipe_id in self.selected_recipes:
            self.selected_recipes.pop(recipe_id)
        else:
            self.selected_recipes[recipe_id] = self.recipes[recipe_id]

    def desired_ingredients(self) -> list[dict]:
        """
        Sums each upc quantity across the selected recipes.
        Ignores ingredients with no upc (empty string)
        :return: [ {'upc': <str>,
                    'quantity': <int>},
                    {..}]
        """
        ingredient_dict: dict = {}
        for recipe_id in self.selected_recipes:
            recipe_ingredients: dict = self.selected_recipes[recipe_id]['ingredients']
            for ingredient_key in recipe_ingredients:
                ingredient = recipe_ingredients[ingredient_key]
                kroger_upc = ingredient['kroger_upc']
                if kroger_upc == '':
                    # No UPC on record
                    continue
                if kroger_upc in ingredient_dict:
                    ingredient_dict[kroger_upc] += ingredient['ingredient_quantity']
                else:
                    ingredient_dict[kroger_upc] = ingredient['ingredient_quantity']
        # Transforming the recipe dict into a list of upc dicts
        order_list: list = []
        for upc in ingredient_dict.keys():
            tmp_dict = {
                'upc': upc,
                'quantity': ingredient_dict[upc]
            }
            order_list.append(tmp_dict)
        # Rounding each float up to the nearest integer
        for upc in order_list:
            original_quant = upc['quantity']
            int_quant = int(original_quant)
            if original_quant != int_quant:
                # Value is a float
                upc['quantity'] = int(1 + original_quant)
            else:
                # Casting to int to eliminate possible floats e.g. 3.0
                upc['quantity'] = int_quant
        return order_list

    def add_ingredient(self, recipe_id: int, ingredient: dict) -> tuple[int, dict]:
        """
        Adds a new ingredient entry in the database.
        Updates Model as well
        :param recipe_id:
        :param ingredient:
                        quantity: Must be > 0,
                        kroger_upc: Must be a 13 digit integer

                        {'ingredient_name': <>,
                        'ingredient_quantity': <>,
                         'ingredient_unit_type': <>,
                         'kroger_upc':  <> }
        """
        # Validating values
        ingredient_quantity: float = ingredient['ingredient_quantity']
        if ingredient_quantity <= 0:
            return -1, {'error_message': f'ingredient_quantity must be >0, not {ingredient_quantity}'}
        ret = self._valid_upc(ingredient['kroger_upc'])
        if ret[0] != 0:
            return ret
        ret = self.db_interface.add_ingredient(recipe_id, ingredient)
        if ret[0] != 0:
            return ret
        # Updating Model
        ingredient_id: int = ret[1]['ingredient_id']
        self.recipes[recipe_id]['ingredients'][ingredient_id] = copy.deepcopy(ingredient)
        self.recipes[recipe_id]['ingredients'][ingredient_id]['ingredient_id'] = ingredient_id
        return ret

    def delete_ingredient(self, recipe_id: int, ingredient_id_dict: dict) -> tuple[int, dict]:
        """
        :param recipe_id:
        :param ingredient_id_dict:  {'ingredient_id': int <> }.
        """
        ingredient_id = ingredient_id_dict['ingredient_id']
        if ingredient_id not in self.recipes[recipe_id]['ingredients']:
            return -1, {'error_message': f'invalid ingredient id: {ingredient_id}'}
        ret = self.db_interface.delete_ingredient(ingredient_id)
        if ret[0] != 0:
            Logger.Logger.log_error(str(ret))
            print(f'Error deleting ingredient:' + ret)
        self.recipes[recipe_id]['ingredients'].pop(ingredient_id)
        return ret

    def retitle_recipe(self, recipe_id: int, new_title_dict: dict) -> tuple[int, dict]:
        """ Update database and Model """
        new_title: str = new_title_dict['new_recipe_title']
        ret = self.db_interface.retitle_recipe(recipe_id, new_title)
        if ret[0] == 0:
            self.recipes[recipe_id]['recipe_title'] = new_title
        return ret

    def update_notes(self, recipe_id: int, noted_dict: dict) -> tuple[int, dict]:
        updated_notes: str = noted_dict['updated_recipe_notes']
        ret = self.db_interface.update_notes(recipe_id, updated_notes)
        if ret[0] == 0:
            self.recipes[recipe_id]['recipe_notes'] = updated_notes
        return ret
