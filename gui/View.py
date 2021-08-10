from tkinter import *
import Controller
from gui.SelectionScrollFrame import SelectionScrollFrame


class View(Tk):

    def __init__(self, controller: Controller):
        super().__init__()
        self.controller: Controller = controller
        recipes: dict = controller.get_recipes()
        self.rowconfigure(0, weight=1)  # Allows the outer scroll frame to stretch vertically
        # Initializing child widgets
        self.SelectionScrollFrame = SelectionScrollFrame(self, 0, 0, recipes)

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

    def on_mousewheel(self, event, side: str):
        """
        :param: side: 'select' or 'detail'
        """
        if side == 'select':
            self.SelectionScrollFrame.canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
        elif side == 'detail':
            # @TODO self.DetailScrollFrame etc.
            pass
