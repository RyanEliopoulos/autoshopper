from tkinter import *


class RecipeDetailHeader:

    """
        This will need:
            PoC for managing recipe name on the detail frame.
            Still requires a mechanism for sending the new name out to the Model and SelectFrame.
    """

    def __init__(self, recipe_name: str, parent):
        self.recipe_str_var: StringVar = StringVar()
        self.recipe_str_var.set(recipe_name)
        self.parent = parent
        self.name_label = self._build_label()
        self.edit_button = self._build_edit_button()

    def _build_label(self) -> Label:
        new_label: Label = Label(self.parent, textvariable=self.recipe_str_var)
        new_label.grid(row=0, column=0)
        return new_label

    def _build_edit_button(self) -> Button:
        new_button: Button = Button(self.parent, text='E', command=self._invoke_edit)
        new_button.grid(row=0, column=1)
        return new_button

    def _invoke_edit(self):
        new_window: Toplevel = Toplevel(height=1000, width=1000)
        new_name_var: StringVar = StringVar()
        new_name_var.set(self.recipe_str_var.get())
        entry_box: Entry = Entry(new_window, textvariable=new_name_var)
        entry_box.grid(row=0, column=0, columnspan=2)
        save_button: Button = Button(new_window, text='SAVE', command=lambda: self._save_edit(new_window
                                                                                              , new_name_var))
        save_button.grid(row=1, column=0)
        discard_button: Button = Button(new_window, text='CANCEL', command=lambda: self._discard_edit(new_window))
        discard_button.grid(row=1, column=1)

    def _save_edit(self, new_window: Toplevel, new_name_var: StringVar):
        """ for use by the edit window 'confirm' button """
        self.recipe_str_var.set(new_name_var.get())
        new_window.destroy()

    def _discard_edit(self, new_window: Toplevel):
        """ for use by the edit window 'cancel' button """
        new_window.destroy()


root = Tk()
rdh = RecipeDetailHeader('my_recipe', root)
root.mainloop()