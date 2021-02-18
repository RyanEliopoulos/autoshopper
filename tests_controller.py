import unittest
import controller


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.xo = controller.Controller()

    def test_read_recipes(self):
        # Testing recipe count
        self.assertTrue(len(self.xo.recipes) == 2)
        # Testing recipe names
        self.assertEqual('bulk burritos', self.xo.recipes[0]['recipe_name'])
        self.assertEqual('fried rice', self.xo.recipes[1]['recipe_name'])

    def test_select_recipe(self):
        # marking "bulk burritos" as selected
        self.xo.select_recipe(0)
        selected_recipe = self.xo.planner.recipes_get_selected()[0]
        self.assertEqual(selected_recipe['recipe_name'], 'bulk burritos')

    def test_deselect_recipe(self):
        # marking "fried rice" as selected
        self.xo.select_recipe(1)
        # deselecting
        self.xo.deselect_recipe(1)
        self.assertEqual(len(self.xo.planner.recipes_get_selected()), 0)

    def test_build_grocery_list(self):
        """
            Tests the call to product_info API and the interleaving of its new information with the
            local values of the grocery list
        """
        # Selecting recipe first (bulk burritos)
        self.xo.select_recipe(0)

        # Retrieving tokens for server communication
        self.xo.customer_communicator.get_tokens()

        # Building list
        grocery_list = self.xo.build_grocery_list()

        # Asserting the right items are in the dictionary
        self.assertTrue("0001111097975" in grocery_list)  # ground beef
        self.assertTrue("0007373100419" in grocery_list)  # tortilla stack
        self.assertTrue("0000000004665" in grocery_list)  # yellow onion
        # Asserting nothing more is present in the list
        self.assertTrue(len(grocery_list) == 3)


        # Checking values returned by product_info API call
        for upc in grocery_list.keys():
            # Checking price value has updated from default
            price = grocery_list[upc]['price']
            self.assertTrue(price != '?')
            # Checking size value has updated from default
            size = grocery_list[upc]['size']
            self.assertTrue(size != '?')

