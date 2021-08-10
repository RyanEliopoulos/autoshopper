from tkinter import *
from gui.errormsg import error_message


class IngredientComponent(Frame):
    """ Container for the 5 widgets every ingredient has:
        1. ingredient_title
        2. ingredient_quantity
        3. measurement_type
        4. kroger_upc
        5. kroger_quantity
    """

    def __init__(self, parent: 'IngredientFrame', column: int, row: int, recipe_id: int, ingredient: dict):
        Frame.__init__(self, parent)
        self.grid(column=column, row=row)
        self.parent = parent
        self.recipe_id: int = recipe_id
        self.ingredient: dict = ingredient
        self.name_label: Label = self.label_factory(ingredient['ingredient_name'],
                                                    0,
                                                    0)
        self.iquantity_label: Label = self.label_factory(ingredient['ingredient_quantity'],
                                                         1,
                                                         0)
        self.mtype_label: Label = self.label_factory(ingredient['ingredient_unit_type'],
                                                     2,
                                                     0)
        self.kroger_upc: Label = self.label_factory(ingredient['kroger_upc'],
                                                    1,
                                                    1)
        self.kroger_quantity: Label = self.label_factory(ingredient['kroger_quantity'],
                                                         2,
                                                         1)
        self.del_button: Button = Button(self, text='X', command=self._delete_ingredient)
        self.del_button.grid(column=3, row=0, rowspan=1)

        # Edit button and delete button
    def label_factory(self, text: str, column: int, row: int) -> Label:
        new_label: Label = Label(self, text=text)
        new_label.grid(column=column, row=row)
        return new_label

    def _delete_ingredient(self):
        # Ask controller to perform the deletion
        root: 'View' = self.winfo_toplevel()
        payload: dict = {'change': 'delete_ingredient',
                                           'parameter': { 'ingredient_id': self.ingredient['ingredient_id']}}
        ret = root.controller.edit_recipe(self.recipe_id, payload)
        if ret[0] != 0:
            error_message(ret)
        else:
            # Successfully deleted ingredient from DB
            self.parent.ingredient_components.pop(self.ingredient['ingredient_id'])
            self.destroy()
