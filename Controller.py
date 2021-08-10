import Communicator
import DBInterface
import Model


class Controller:

    def __init__(self, db_path: str):
        self.db_interface = DBInterface.DBInterface(db_path)
        self.communicator = Communicator.Communicator(self.db_interface)
        # @TODO Check if communicator is working, else disable API features but work otherwise
        self.model = Model.Model(self.db_interface)

    def new_recipe(self) -> tuple[int, dict]:
        """ Returns the recipe_id upon success """
        return self.model.new_recipe()

    def delete_recipe(self, recipe_id: int) -> tuple[int, dict]:
        """ Returns """
        return self.model.delete_recipe(recipe_id)

    def get_recipes(self) -> dict:
        """ Send all recipe data to the caller  """
        return self.model.recipes

    def toggle_recipe(self, recipe_id: int) -> None:
        """ (de)select a given recipe """
        self.model.toggle_recipe(recipe_id)

    def edit_recipe(self, recipe_id: int, change: dict) -> tuple[int, dict]:
        """
        :param recipe_id
        :param change: {'change': <valid_changes> str,
                         'parameter': <arg for fnx calls>
        :return:
        """
        valid_changes = {
            'add_ingredient': self.model.add_ingredient,
            'delete_ingredient': self.model.delete_ingredient,
            'rename_recipe': self.model.retitle_recipe,
            'update_notes': self.model.update_notes
        }
        desired_change: str = change['change']
        if desired_change not in valid_changes.keys():
            return -1, {'error_message': f'Failed to edit {recipe_id}: {change} is not valid'}
        return valid_changes[desired_change](recipe_id, change)

    def load_cart(self) -> tuple[int, dict]:
        """
        Query model to return a list of ingredients based on
        all of the selected recipes. Hand off to Communicator.
        Inform View of the outcome.
        :return:
        """
        shopping_list: list = self.model.desired_ingredients()
        return self.communicator.add_to_cart(shopping_list)

