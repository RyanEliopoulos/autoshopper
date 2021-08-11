from tkinter import *
import Controller
from gui.SelectionScrollFrame import SelectionScrollFrame
from gui.DetailScrollFrame import DetailScrollFrame
from gui.errormsg import error_message


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
        mn.add_command(label='Delete Recipe', command=self._delete_confirmation)
        mn.add_command(label='Load Cart', command=self.controller.load_cart)

    def _new_recipe(self):
        # Requesting new recipe from the controller
        ret = self.controller.new_recipe()
        if ret[0] == -1:
            error_message(ret)
        else:
            new_recipe: dict = ret[1]
            active_recipe: 'DetailFrame' = self.DetailScrollFrame.visible_frame  # pulled for select's benefit
            self.DetailScrollFrame.new_recipe(new_recipe)
            self.SelectionScrollFrame.add_recipe(active_recipe, new_recipe)
            print(ret)

    def _delete_confirmation(self):
        if self.SelectionScrollFrame.highlighted_frame is None:
            print('No recipe is currently selected')
            error_message('No recipe is currently selected')
            return
        recipe_title: str = self.SelectionScrollFrame.highlighted_frame.recipe['recipe_title']
        """ Opens a dialog box allowing user to confirm/deny proper usage of the delete button """
        new_window: Toplevel = Toplevel(height=300, width=300)
        name_label: Label = Label(new_window, text=f'delete {recipe_title}?')
        name_label.grid(column=0, row=0, columnspan=2)
        ok_button: Button = Button(new_window, text='Confirm', command=lambda: self._delete_recipe(new_window))
        ok_button.grid(column=0, row=1)
        cancel_button: Button = Button(new_window, text='Cancel', command=lambda: new_window.destroy())
        cancel_button.grid(column=1, row=1)

    def _delete_recipe(self, confirmation_window: Toplevel):
        confirmation_window.destroy()
        # Checking for selected recipe
        recipe_id: int = self.DetailScrollFrame.visible_frame.recipe_id
        ret = self.controller.delete_recipe(recipe_id)
        if ret[0] == -1:
            error_message(ret)
            return
        self.SelectionScrollFrame.delete_recipe(recipe_id)
        self.DetailScrollFrame.delete_recipe()

    def update_detail_frame(self, recipe_id):
        self.DetailScrollFrame.make_visible(recipe_id)