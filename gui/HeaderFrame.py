from tkinter import *
from gui.errormsg import error_message


class HeaderFrame(Frame):
    """ Don't think I need to worry about size of this widget.
        Just has to be big enough to accommodate the label (whose font size is adjustable) and the edit button
    """

    def __init__(self,
                 parent: Frame,
                 column: int,
                 row: int,
                 recipe_name: str,
                 recipe_id: int):
        Frame.__init__(self, parent)
        self.grid(column=column, row=row)
        self.parent: Frame = parent
        self.recipe_name: str = recipe_name
        self.recipe_id: int = recipe_id
        # Building label
        self.label: Label = Label(self, text=recipe_name)
        self.label.grid(column=0, row=0)
        # Building edit button
        self.edit_button: Button = Button(self, text='E', command=self._edit_header)
        self.edit_button.grid(column=1, row=0)

    def _edit_header(self):
        # Opens the new window containing the entry fields
        edit_window: Toplevel = Toplevel(height=1000, width=1000)
        str_var: StringVar = StringVar()
        str_var.set(self.recipe_name)
        entry_button: Entry = Entry(edit_window, textvariable=str_var)
        entry_button.grid(column=0, row=0, columnspan=1)
        ok_button: Button = Button(edit_window, text='OK', command=lambda: self._update_name(str_var.get(),
                                                                                             edit_window))
        ok_button.grid(column=0, row=1)
        cancel_button: Button = Button(edit_window, text='Cancel', command=lambda: edit_window.destroy())
        cancel_button.grid(column=1, row=1)

    def _update_name(self, new_name: str, edit_window: Toplevel):
        # Requesting change with controller
        root: 'View' = self.winfo_toplevel()
        ret = root.controller.edit_recipe(self.recipe_id, {'change': 'rename_recipe',
                                                           'parameter': new_name})
        if ret[0] != 0:
            error_message(ret[1])
            print(ret)
        else:
            self.recipe_name = new_name
            self.label.configure(text=self.recipe_name)
            # Updating SelectFrame
            select_frame: 'SelectFrame' = root.SelectionScrollFrame.select_frames[self.recipe_id]
            select_frame.label.configure(text=self.recipe_name)
        edit_window.destroy()

