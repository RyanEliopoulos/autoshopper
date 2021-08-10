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
        mn.add_command(label='Delete Recipe', command=self._delete_recipe)

    def _new_recipe(self):
        # Requesting new recipe from the controller
        ret = self.controller.new_recipe()
        if ret[0] == -1:
            print("Someting went wrong creating a new recipe" + str(ret))
        else:
            new_recipe: dict = ret[1]['recipe']
            print('something went right creating a new recipe')
            active_recipe: 'DetailFrame' = self.DetailScrollFrame.visible_frame  # pulled for select's benefit
            self.DetailScrollFrame.new_recipe(new_recipe)
            self.SelectionScrollFrame.add_recipe(active_recipe, new_recipe)
            print(ret)

    def _delete_recipe(self):
        # Checking for selected recipe
        if self.DetailScrollFrame.visible_frame is None:
            print('No recipe is currently selected')
            return
        recipe_id: int = self.DetailScrollFrame.visible_frame.recipe_id
        ret = self.controller.delete_recipe(recipe_id)
        if ret[0] == -1:
            print(f'Encountered an error deleting {recipe_id}: {ret}')
            return
        self.SelectionScrollFrame.delete_recipe(recipe_id)
        self.DetailScrollFrame.delete_recipe()
        print(f'Successfully deleted recipe: {recipe_id}')

    def update_detail_frame(self, recipe_id):
        self.DetailScrollFrame.make_visible(recipe_id)