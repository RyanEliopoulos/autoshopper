import unittest
import view


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.view = view.View()

    def test_init_option_slots(self):
        # Establishing each slot is present in the constructed option_slot dictionary
        for slot in self.view.slot_titles:
            self.assertTrue(slot in self.view.option_slots)
        # Establishing nothing outside the slot_title list made it in
        for key in self.view.option_slots:
            self.assertTrue(key in self.view.slot_titles)

        # Checking the coordinates now
        for index, title in enumerate(self.view.slot_titles):
            # Establishing expected position
            expected_x_coord = self.view.cursor_anchor[0]
            expected_y_coord = self.view.cursor_anchor[1] + index + 1

            # Evaluating actual position
            option_slot = self.view.option_slots[title]
            self.assertEqual(option_slot['coords'][0], expected_x_coord)  # x coord
            self.assertEqual(option_slot['coords'][1], expected_y_coord)  # y coord

    def test_update_option_slots(self):

        options = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth']
        left_index = 0
        right_index = 5
        expected_ret = {'a': 4,
                        's': 3,
                        'd': 2,
                        'f': 1,
                        'g': 0}

        ret_dict = self.view._update_option_slots(options, left_index, right_index)
        # Evaluating initial return dictionary mapping slot titles to their respective option index
        self.assertEqual(expected_ret, ret_dict)
        # Evaluating view.option_slot text
        for title in ret_dict:
            expected_string = options[ret_dict[title]]
            actual_string = self.view.option_slots[title]['text']
            self.assertEqual(expected_string, actual_string)

        # Evaluating pagination
        left_index += 5
        right_index += 5
        ret_dict = self.view._update_option_slots(options, left_index, right_index)
        expected_ret = {'g': 5}
        self.assertEqual(expected_ret, ret_dict)

        # Evaluating updated view.option_slot text
        for title in expected_ret:
            if title != 'g':
                self.assertIsNone(self.view.option_slots[title]['text'])
            else:
                self.assertEqual('sixth', self.view.option_slots[title]['text'])


