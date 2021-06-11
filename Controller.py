# Project components
import Communicator
import DBInterface
import Model


class Controller:

    def __init__(self, db_path: str):
        self.db_interface = DBInterface.DBInterface(db_path)
        self.communicator = Communicator.Communicator(self.db_interface)
        # @TODO Check if communicator is working, else disable API features but work otherwise
        self.model = Model.Model(self.db_interface)

    def add_recipe(self, recipe: dict) -> tuple[int, dict]:
        return self.model.add_recipe(recipe)

    def delete_recipe(self, recipe_id: int) -> tuple[int, dict]:
        return self.model.delete_recipe(recipe_id)

    def get_recipes(self) -> dict:
        """ Send all recipe data to the caller  """
        return self.model.recipes

    def toggle_recipe(self, recipe_id: int) -> None:
        """ (de)select a given recipe """
        self.model.toggle_recipe(recipe_id)

    def edit_recipe(self):
        """
        Pass a list of changes made to a particular recipe,
        then "commit" them in order?
        :return:
        """
        ...

    def load_cart(self) -> tuple[int, dict]:
        """
        Query model to return a list of ingredients based on
        all of the selected recipes. Hand off to Communicator.
        Inform View of the outcome.
        :return:
        """
        shopping_list: list = self.model.desired_ingredients()
        return self.communicator.add_to_cart(shopping_list)

