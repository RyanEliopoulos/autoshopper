from tkinter import *
import Controller
from gui.SelectionScrollFrame import SelectionScrollFrame
from gui.DetailScrollFrame import DetailScrollFrame


class View(Tk):

    def __init__(self, controller: Controller):
        super().__init__()
        self.controller: Controller = controller
        self.rowconfigure(0, weight=1)  # Allows the outer scroll frame to stretch vertically
        recipes: dict = controller.get_recipes()
        # Initializing child widgets
        self.SelectionScrollFrame = SelectionScrollFrame(self, 0, 0, recipes)
        self.DetailScrollFrame: DetailScrollFrame = DetailScrollFrame(self, 1, 0, recipes)
        self._build_menubuttons()
        self.mainloop()

    def _build_menubuttons(self):
        mn = Menu(self)
        self.config(menu=mn)
        mn.add_command(label='New Recipe', command=self._new_recipe)

    def _new_recipe(self):
        # Requesting new recipe from the controller
        ret = self.controller.new_recipe()
        if ret[0] == -1:
            print("Someting went wrong")
        else:
            print('something went right')
            print(ret)

    def update_detail_frame(self, recipe_id: int):
        self.DetailScrollFrame.make_visible(recipe_id)