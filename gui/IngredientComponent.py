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
        self.edit_button:Button = Button(self,
                                         text='E',
                                         command=lambda: self._edit_ingredients(self.ingredient['ingredient_name'],
                                                                                self.ingredient['ingredient_quantity'],
                                                                                self.ingredient['ingredient_unit_type'],
                                                                                self.ingredient['kroger_upc'],
                                                                                self.ingredient['kroger_quantity']))
        self.edit_button.grid(column=3, row=0)
        self.del_button: Button = Button(self,
                                         text='X',
                                         command=lambda: self._delete_confirmation(self.ingredient['ingredient_name']))
        self.del_button.grid(column=4, row=0, rowspan=1)
        self._bind_scrolling()

    def label_factory(self, text: str, column: int, row: int) -> Label:
        new_label: Label = Label(self, text=text)
        new_label.grid(column=column, row=row)
        return new_label

    def _bind_scrolling(self):
        self.bind('<Enter>', lambda evnt: evnt.widget.bind('<MouseWheel>', self.parent.parent.dsf.on_mousewheel))
        self.bind('<Leave>', lambda evnt: evnt.widget.unbind_all('<MouseWheel>'))
        self.name_label.bind('<Enter>', lambda evnt: evnt.widget.bind('<MouseWheel>', self.parent.parent.dsf.on_mousewheel))
        self.name_label.bind('<Leave>', lambda evnt: evnt.widget.unbind_all('<MouseWheel>'))
        self.iquantity_label.bind('<Enter>', lambda evnt: evnt.widget.bind('<MouseWheel>', self.parent.parent.dsf.on_mousewheel))
        self.iquantity_label.bind('<Leave>', lambda evnt: evnt.widget.unbind_all('<MouseWheel>'))
        self.mtype_label.bind('<Enter>', lambda evnt: evnt.widget.bind('<MouseWheel>', self.parent.parent.dsf.on_mousewheel))
        self.mtype_label.bind('<Leave>', lambda evnt: evnt.widget.unbind_all('<MouseWheel>'))
        self.kroger_upc.bind('<Enter>', lambda evnt: evnt.widget.bind('<MouseWheel>', self.parent.parent.dsf.on_mousewheel))
        self.kroger_upc.bind('<Leave>', lambda evnt: evnt.widget.unbind_all('<MouseWheel>'))
        self.kroger_quantity.bind('<Enter>', lambda evnt: evnt.widget.bind('<MouseWheel>', self.parent.parent.dsf.on_mousewheel))
        self.kroger_quantity.bind('<Leave>', lambda evnt: evnt.widget.unbind_all('<MouseWheel>'))
        self.del_button.bind('<Enter>', lambda evnt: evnt.widget.bind('<MouseWheel>', self.parent.parent.dsf.on_mousewheel))
        self.del_button.bind('<Leave>', lambda evnt: evnt.widget.unbind_all('<MouseWheel>'))
        self.edit_button.bind('<Enter>', lambda evnt: evnt.widget.bind('<MouseWheel>', self.parent.parent.dsf.on_mousewheel))
        self.edit_button.bind('<Leave>', lambda evnt: evnt.widget.unbind_all('<MouseWheel>'))

    def _edit_ingredients(self,
                          ingredient_name: str,
                          ingredient_quantity: float,
                          ingredient_unit_type: str,
                          kroger_upc: str,
                          kroger_quantity: float):

        """ Opens a window with entry widgets for editing """
        new_window: Toplevel = Toplevel(height=1000, width=1000)
        # Row 1 - ingredient name
        name_label: Label = Label(new_window, text='Ingredient name')
        name_label.grid(column=0, row=0)
        temp_iname: StringVar = StringVar()
        temp_iname.set(ingredient_name)
        name_entry: Entry = Entry(new_window, textvariable=temp_iname)
        name_entry.grid(column=1, row=0)
        # Row 2 - ingredient quantity
        iquant_label: Label = Label(new_window, text='Quantity')
        iquant_label.grid(column=0, row=1)
        temp_iquantity: DoubleVar = DoubleVar()
        temp_iquantity.set(ingredient_quantity)
        iquant_entry: Entry = Entry(new_window, textvariable=temp_iquantity)
        iquant_entry.grid(column=1, row=1)
        # Row 3 - measure type
        mtype_label: Label = Label(new_window, text='Measure type')
        mtype_label.grid(column=0, row=2)
        temp_mtype: StringVar = StringVar()
        temp_mtype.set(ingredient_unit_type)
        mtype_entry: Entry = Entry(new_window, textvariable=temp_mtype)
        mtype_entry.grid(column=1, row=2)
        # Row 4 - Kroger UPC
        kupc_label: Label = Label(new_window, text='Kroger UPC')
        kupc_label.grid(column=0, row=3)
        temp_kupc: StringVar = StringVar()
        temp_kupc.set(kroger_upc)
        kupc_entry: Entry = Entry(new_window, textvariable=temp_kupc)
        kupc_entry.grid(column=1, row=3)
        # Row 5 - Kroger quantity
        kquant_label: Label = Label(new_window, text='Kroger quantity')
        kquant_label.grid(column=0, row=4)
        temp_kquant: DoubleVar = DoubleVar()
        temp_kquant.set(kroger_quantity)
        kquant_entry: Entry = Entry(new_window, textvariable=temp_kquant)
        kquant_entry.grid(column=1, row=4)
        # Row 6 - Save/Discard buttons
        save_button: Button = Button(new_window, text='Save', command=lambda: self._save_edit(temp_iname.get(),
                                                                                              temp_iquantity.get(),
                                                                                              temp_mtype.get(),
                                                                                              temp_kupc.get(),
                                                                                              temp_kquant.get(),
                                                                                              new_window))
        save_button.grid(column=0, row=5)
        discard_button: Button = Button(new_window, text='Discard', command=lambda: new_window.destroy())
        discard_button.grid(column=1, row=5)

    def _save_edit(self,
                   ingredient_name: str,
                   ingredient_quantity: float,
                   ingredient_unit_type: str,
                   kroger_upc: str,
                   kroger_quantity: float,
                   edit_window: Toplevel):
        """ Saves the contents from the edit window """
        ingredient_dict: dict = {
            'ingredient_id': self.ingredient['ingredient_id'],
            'ingredient_name': ingredient_name,
            'ingredient_quantity': ingredient_quantity,
            'ingredient_unit_type': ingredient_unit_type,
            'kroger_upc': kroger_upc,
            'kroger_quantity': kroger_quantity,
        }
        root: 'View' = self.winfo_toplevel()
        # Packaging for controller
        payload: dict = {
            'change': 'update_ingredient',
            'parameter': ingredient_dict
        }
        ret = root.controller.edit_recipe(self.recipe_id, payload)
        if ret[0] != 0:
            error_message(ret)
        else:
            # Updating labels
            self.name_label.config(text=ingredient_name)
            self.iquantity_label.config(text=ingredient_quantity)
            self.mtype_label.config(text=ingredient_unit_type)
            self.kroger_upc.config(text=kroger_upc)
            self.kroger_quantity.config(text=kroger_quantity)
            self.ingredient = ingredient_dict
        edit_window.destroy()

    def _delete_confirmation(self, ingredient_name: str):
        """ Opens a dialog box allowing user to confirm/deny proper usage of the delete button """
        new_window: Toplevel = Toplevel(height=300, width=300)
        name_label: Label = Label(new_window, text=f'delete {ingredient_name}?')
        name_label.grid(column=0, row=0, columnspan=2)
        ok_button: Button = Button(new_window, text='Confirm', command=lambda: self._delete_ingredient(new_window))
        ok_button.grid(column=0, row=1)
        cancel_button: Button = Button(new_window, text='Cancel', command=lambda: new_window.destroy())
        cancel_button.grid(column=1, row=1)

    def _delete_ingredient(self, confirmation_window: Toplevel):
        confirmation_window.destroy()
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
