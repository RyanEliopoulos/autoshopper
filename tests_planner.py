import unittest
from planner import Planner
import json


class PlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        with open('test_recipes.json', 'r') as recipe_file:
            recipes = json.load(recipe_file)
        self.planner = Planner(recipes)

    def test_init(self):
        self.assertEqual(len(self.planner.recipes), 2)

    def test_recipe_select(self):
        self.planner.recipes_select(1)
        selected_recipes = self.planner.recipes_get_selected()
        self.assertEqual(selected_recipes[0], self.planner.recipes[1])
        self.assertEqual('fried rice', selected_recipes[0]['recipe_name'])

    def test_recipe_deselect(self):
        self.planner.recipes_deselect(1)
        selected_recipes = self.planner.recipes_get_selected()
        self.assertEqual(len(selected_recipes), 0)

    def test_tallyitems(self):
        self.planner.recipes_select(0)
        selected_recipes = self.planner.recipes_get_selected()
        recipe = selected_recipes[0]
        tallied_items = self.planner.recipe_tallyitems(recipe)
        # Checking quantities
        self.assertEqual(tallied_items['0007373100415']['quantity'], 4)
        self.assertEqual(tallied_items['0001111097975']['quantity'], 3)
        # Checking names
        self.assertEqual('ground beef', tallied_items['0001111097975']['colloquial_name'])
        self.assertEqual('tortilla stack', tallied_items['0007373100415']['colloquial_name'])

    def test_grocery_buildorder(self):
        # staging recipes
        self.planner.recipes_select(0)
        self.planner.recipes_select(1)
        self.planner.grocery_buildfrom_selected()

        # Testing ground beef quantity
        self.assertEqual(self.planner.grocery_order['0001111097975']['colloquial_name'], 'ground beef')
        self.assertEqual(self.planner.grocery_order['0001111097975']['quantity'], 3)

        # Testing calrose rice
        self.assertEqual(self.planner.grocery_order['0001115214409']['colloquial_name'], 'calrose rice')
        self.assertEqual(self.planner.grocery_order['0001115214409']['quantity'], 1)

        # Testing shared item (yellow onion)
        self.assertEqual(self.planner.grocery_order['0000000004665']['colloquial_name'], 'yellow onion')
        self.assertEqual(self.planner.grocery_order['0000000004665']['quantity'], 2)

    def test_grocery_subtractfrom(self):
        # Staging recipes
        self.planner.recipes_select(0)
        self.planner.recipes_select(1)
        self.planner.grocery_buildfrom_selected()

        # Testing subtraction (yellow onion, halving)
        self.planner.grocery_subtractfrom('0000000004665', 1)
        self.assertEqual(self.planner.grocery_order['0000000004665']['quantity'], 1)

        # Testing complete removal (yellow onion)
        self.planner.grocery_subtractfrom('0000000004665', 1)
        self.assertRaises(KeyError, self.planner.grocery_subtractfrom, '0000000004665', 3)




