# Project components
import Communicator
import DBInterface
# Other modules
import json
import time
import os
import copy


class Controller:

    def __init__(self, db_path: str):
        self.db_interface = DBInterface.DBInterface(db_path)
        self.communicator = Communicator.Communicator(self.db_interface)
        # @TODO Check if communicator is working, else disable API features but work otherwise
        # self.model = Model.Model(self.db_interface)

    def get_recipes(self):
        """
        Send all recipe data to the caller (view)
        :return:
        """
        ...

    def toggle_recipe(self):
        """
        (de)select a given recipe
        :return:
        """
        ...

    def edit_recipe(self):
        """
        Pass a list of changes made to a particular recipe,
        then "commit" them in order?
        :return:
        """
        ...

    def load_cart(self):
        """
        Query model to return a list of ingredients based on
        all of the selected recipes. Hand off to Communicator.
        Inform View of the outcome.
        :return:
        """
        ...
