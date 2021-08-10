from tkinter import *
from gui.HeaderFrame import HeaderFrame
from gui.IngredientFrame import IngredientFrame


class DetailFrame(Frame):
    """ Every recipe has a DetailFrame responsible for providing the details of the recipes (right-hand side)
        Not really implemented at all (8/9/2021).

        Remember to address sizing!
    """

    def __init__(self, parent: 'DetailScrollFrame', recipe: dict):
        """ recipe: {'ingredient_title': <>, 'recipe_id': <>, etc.. }
        """

        self.recipe_id: int = recipe['recipe_id']
        Frame.__init__(self, parent, width=300, height=300)
        self.grid(column=0, row=0)
        self.grid_remove()
        self.config(background='purple')
        self.grid_propagate(False)
        self.visible: bool = False
        # Building detail contents
        self.hf: HeaderFrame = HeaderFrame(self,
                                           column=0,
                                           row=0,
                                           recipe_name=recipe['recipe_title'],
                                           recipe_id=self.recipe_id)
        self.ing_frame: IngredientFrame = IngredientFrame(self, 0, 1, recipe)

    def toggle_visibility(self):
        if self.visible:
            self.grid_remove()
            self.visible = False
        else:
            self.grid()
            self.visible = True