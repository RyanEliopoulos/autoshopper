import unittest
from planner import Planner
import json


class PlannerTests(unittest.TestCase):
    """
        Planner relies on the ingredient UPC for testing. Product id is not used
    """
    def setUp(self) -> None:
        with open('test_recipes.json', 'r') as recipe_file:
            recipes = json.load(recipe_file)
        self.planner = Planner(recipes)

    def test_init(self):
        self.assertEqual(len(self.planner.recipes), 6)

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
        self.assertEqual(tallied_items['0007373100419']['quantity'], 3.5)
        self.assertEqual(tallied_items['0001111097975']['quantity'], 3)
        # Checking names
        self.assertEqual('ground beef', tallied_items['0001111097975']['colloquial_name'])
        self.assertEqual('tortilla stack', tallied_items['0007373100419']['colloquial_name'])

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

        # Testing rounded item (tortilla stacks)
        self.assertEqual(self.planner.grocery_order['0007373100419']['colloquial_name'], 'tortilla stack')
        self.assertEqual(self.planner.grocery_order['0007373100419']['quantity'], 4)

    def test_grocery_modifyquantity(self):
        # Staging recipes
        self.planner.recipes_select(0)
        self.planner.recipes_select(1)
        self.planner.grocery_buildfrom_selected()

        # Testing subtraction (yellow onion, halving)
        self.planner.grocery_modifyquantity('0000000004665', -1)
        self.assertEqual(self.planner.grocery_order['0000000004665']['quantity'], 1)

        # Testing complete removal (yellow onion)
        self.planner.grocery_modifyquantity('0000000004665', -1)
        self.assertRaises(KeyError, self.planner.grocery_modifyquantity, '0000000004665', 3)

        # Testing addition (ground beef)
        self.planner.grocery_modifyquantity('0001111097975', 1)
        self.assertEqual(self.planner.grocery_order['0001111097975']['quantity'], 4)

    def test_new_recipe(self):
        # Testing a new recipe whose name is unused.
        recipe_name = "available name"
        ret = self.planner.recipe_new_recipe(recipe_name)
        self.assertTrue(ret)
        # Ensuring the appropriate data structure was created
        new_recipe_struct = {
            'recipe_name': recipe_name
            , 'recipe_items': []
            , 'selected': 0
        }
        self.assertEqual(new_recipe_struct, self.planner.new_recipe)

        # Testing a name already used
        recipe_name = 'bulk burritos'
        ret = self.planner.recipe_new_recipe(recipe_name)
        self.assertFalse(ret)

    def test_newrecipe_additem(self):
        # Building new recipe
        recipe_name = "bake potatoes"
        ret = self.planner.recipe_new_recipe(recipe_name)
        self.assertTrue(ret)

        # Adding item not already present
        new_item = {"colloquial_name": "yellow onion",
                    "product_id": "0000000004665",
                    "upc": "0000000004665",
                    "quantity": "1"}
        ret = self.planner.recipe_newrecipe_additem(new_item)
        self.assertTrue(ret)
        # Verifying presence of new recipe item
        self.assertEqual(new_item, self.planner.new_recipe['recipe_items'][0])

        # Attempting to add duplicate colloquial_name
        duplicate_item = {"colloquial_name": "yellow onion",
                          "product_id": "0000000004665",
                          "upc": "0000000004665",
                          "quantity": "1"}
        ret = self.planner.recipe_newrecipe_additem(duplicate_item)
        self.assertFalse(ret)

    def test_recipe_newrecipe_modifyitem(self):
        # Building new recipe
        recipe_name = "shawarma"
        ret = self.planner.recipe_new_recipe(recipe_name)
        self.assertTrue(ret)

        # Adding item not already present
        new_item = {"colloquial_name": "yellow onion",
                    "product_id": "0000000004665",
                    "upc": "0000000004665",
                    "quantity": "1"}
        ret = self.planner.recipe_newrecipe_additem(new_item)
        self.assertTrue(ret)

        # Checking positive quantity update
        self.planner.recipe_newrecipe_modifyitem('yellow onion', 4)
        updated_quantity = self.planner.new_recipe['recipe_items'][0]['quantity']
        self.assertEqual(4, updated_quantity)

        # Checking non-positive quantity update (deletion)
        self.planner.recipe_newrecipe_modifyitem('yellow onion', 0)
        recipe_item_count = len(self.planner.new_recipe['recipe_items'])
        self.assertEqual(0, recipe_item_count)

    def test_newrecipe_save(self):
        # Building new recipe
        recipe_name = "onion rings"
        ret = self.planner.recipe_new_recipe(recipe_name)
        self.assertTrue(ret)
        pre_count = len(self.planner.recipes)

        # Adding item not already present
        new_item = {"colloquial_name": "yellow onion",
                    "product_id": "0000000004665",
                    "upc": "0000000004665",
                    "quantity": "1"}
        ret = self.planner.recipe_newrecipe_additem(new_item)
        self.assertTrue(ret)
        self.planner.recipe_newrecipe_save()
        post_count = len(self.planner.recipes)
        # Checking change in recipe count
        self.assertEqual(1 + pre_count, post_count)

    def test_playing(self):

        recipes = self.planner.recipes
        my_recipe = recipes[0]
        my_recipe['selected'] = 1

        select_recipes = self.planner.recipes_get_selected()
        print(select_recipes)


        grocery = self.planner.grocery_buildfrom_selected()
        print(grocery)