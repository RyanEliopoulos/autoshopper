from tkinter import *


class IngredientDetailContainer(Frame):
    """
        Responsible for managing the IngredientDetail objects, which hold all of the widgets
        to display/modify existing ingredients.
    """

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        # Gridding ourself
        self.grid(column=0, row=0)
        self.ingredient_count: int = 0
        self.ingredient_dict: dict = dict()

        # New ingredient button
        add_ing_button: Button = Button(self, text='+Ingredient', command=self._build_ingredient)
        add_ing_button.grid(column=0, row=0, sticky=W, pady=20)

    def _build_ingredient(self):
        """  Opens the input window for the ingredient


            I probably just need an "EditIngredient" class or something to simplify this.
        """
        new_window: Toplevel = Toplevel(height=1000, width=1000)
        # Row 1 - ingredient name
        name_label: Label = Label(new_window, text='Ingredient name')
        name_label.grid(column=0, row=0)
        name_strvar: StringVar = StringVar()
        name_strvar.set('<name>')
        name_entry: Entry = Entry(new_window, textvariable=name_strvar)
        name_entry.grid(column=1, row=0)
        # Row 2 - ingredient quantity
        iquant_label: Label = Label(new_window, text='Quantity')
        iquant_label.grid(column=0, row=1)
        iquant_dblvar: DoubleVar = DoubleVar()
        iquant_dblvar.set(0.0)
        iquant_entry: Entry = Entry(new_window, textvariable=iquant_dblvar)
        iquant_entry.grid(column=1, row=1)
        # Row 3 - measure type
        mtype_label: Label = Label(new_window, text='Measure type')
        mtype_label.grid(column=0, row=2)
        mtype_strvar: StringVar = StringVar()
        mtype_strvar.set('<Cups/Teaspoons/etc>')
        mtype_entry: Entry = Entry(new_window, textvariable=mtype_strvar)
        mtype_entry.grid(column=1, row=2)
        # Row 4 - Kroger UPC
        kupc_label: Label = Label(new_window, text='Kroger UPC')
        kupc_label.grid(column=0, row=3)
        kupc_strvar: StringVar = StringVar()
        kupc_strvar.set('0000000000000')
        kupc_entry: Entry = Entry(new_window, textvariable=kupc_strvar)
        kupc_entry.grid(column=1, row=3)
        # Row 5 - Kroger quantity
        kquant_label: Label = Label(new_window, text='Kroger quantity')
        kquant_label.grid(column=0, row=4)
        kquant_dblvar: DoubleVar = DoubleVar()
        kquant_dblvar.set(0.0)
        kquant_entry: Entry = Entry(new_window, textvariable=kquant_dblvar)
        kquant_entry.grid(column=1, row=4)
        # Row 6 - Save/Discard buttons
        save_button: Button = Button(new_window, text='Save', command=lambda: self._save(name_strvar.get(),
                                                                                         iquant_dblvar.get(),
                                                                                         mtype_strvar.get(),
                                                                                         kupc_strvar.get(),
                                                                                         kquant_dblvar.get(),
                                                                                         new_window))
        save_button.grid(column=0, row=5)
        discard_button: Button = Button(new_window, text='Discard', command=lambda: self._discard(new_window))
        discard_button.grid(column=1, row=5)
        print("thanks")

    def _save(self,
              ingredient_name: str,
              ingredient_quantity: float,
              measure_type: str,
              kroger_upc: str,
              kroger_quantity: float,
              build_window: Toplevel):
        """ Saves the new ingredient under construction """
        # (Call to Model and evaluation of return status.)
        # Trigger warning windows here

        build_window.destroy()
        # Creating the widgets for a successfully created ingredient
        self.ingredient_count += 1
        new_detail = IngredientDetail(self,
                                      self.ingredient_count,
                                      ingredient_name,
                                      ingredient_quantity,
                                      measure_type,
                                      kroger_upc,
                                      kroger_quantity)
        self.ingredient_dict[self.ingredient_count] = new_detail

    def _discard(self, new_window: Toplevel):
        """ As opposed to saving the candidate for new ingredient """
        new_window.destroy()

    def delete_ingredient_detail(self, detail_id: int):
        """ removes an entry from the self.ingredient dictionary"""
        # Need to shift all of the entries down one in the GUI .grid rows.
        for x in range(detail_id, self.ingredient_count):
            self.ingredient_dict[x] = self.ingredient_dict[x + 1]
            self.ingredient_dict[x].grid(row=x)
        self.ingredient_count -= 1


class IngredientDetail(Frame):

    def __init__(self, parent,
                 detail_id: int,
                 ingredient_name: str,
                 ingredient_quantity: float,
                 measure_type: str,
                 kroger_upc: str,
                 kroger_quantity: float):
        Frame.__init__(self, parent)
        self.grid(column=0, row=(detail_id + 1))
        self.parent = parent
        self.detail_id: int = detail_id  # So the parent object knows what to delete.
        # Control variables from params
        self.iname_strvar: StringVar = StringVar()
        self.iname_strvar.set(ingredient_name)
        self.iquantity_dvar: DoubleVar = DoubleVar()
        self.iquantity_dvar.set(ingredient_quantity)
        self.mtype_strvar: StringVar = StringVar()
        self.mtype_strvar.set(measure_type)
        self.kupc_strvar: StringVar = StringVar()
        self.kupc_strvar.set(kroger_upc)
        self.kquantity_dvar: DoubleVar = DoubleVar()
        self.kquantity_dvar.set(kroger_quantity)

        # Info widgets
        self.iname_widget: Label = Label(self, textvariable=self.iname_strvar)
        self.iname_widget.grid(column=0, row=0)
        self.iquantity_widget: Label = Label(self, textvariable=self.iquantity_dvar)
        self.iquantity_widget.grid(column=1, row=0)
        self.mtype_widget: Label = Label(self, textvariable=self.mtype_strvar)
        self.mtype_widget.grid(column=2, row=0)
        self.kupc_widget: Label = Label(self, textvariable=self.kupc_strvar)
        self.kupc_widget.grid(column=1, row=1)
        self.kquantity_widget: Label = Label(self, textvariable=self.kquantity_dvar)
        self.kquantity_widget.grid(column=2, row=1)

        # Mod widgets
        self.edit_button: Button = Button(self, text='E', command=self._edit_ingredient)
        self.edit_button.grid(column=3, row=0, rowspan=2)
        self.delete_button: Button = Button(self,
                                            text='X',
                                            command=lambda: self._delete_confirmation(self.iname_strvar.get()))
        self.delete_button.grid(column=4, row=0, rowspan=2)

    def _delete_confirmation(self, ingredient_name: str):
        """ Opens a dialog box allowing user to confirm/deny proper usage of the delete button """
        new_window: Toplevel = Toplevel(height=300, width=300)
        name_label: Label = Label(new_window, text=f'delete {ingredient_name}?')
        name_label.grid(column=0, row=0, columnspan=2)
        ok_button: Button = Button(new_window, text='Confirm', command=lambda: self._self_destroy(new_window))
        ok_button.grid(column=0, row=1)
        cancel_button: Button = Button(new_window, text='Cancel', command=lambda: new_window.destroy())
        cancel_button.grid(column=1, row=1)

    def _self_destroy(self, confirmation_window: Toplevel):
        self.parent.delete_ingredient_detail(self.detail_id)

        confirmation_window.destroy()
        self.destroy()

    def _edit_ingredient(self):
        new_window: Toplevel = Toplevel(height=1000, width=1000)
        # Row 1 - ingredient name
        name_label: Label = Label(new_window, text='Ingredient name')
        name_label.grid(column=0, row=0)
        temp_iname: StringVar = StringVar()
        temp_iname.set(self.iname_strvar.get())
        name_entry: Entry = Entry(new_window, textvariable=temp_iname)
        name_entry.grid(column=1, row=0)
        # Row 2 - ingredient quantity
        iquant_label: Label = Label(new_window, text='Quantity')
        iquant_label.grid(column=0, row=1)
        temp_iquantity: DoubleVar = DoubleVar()
        temp_iquantity.set(self.iquantity_dvar.get())
        iquant_entry: Entry = Entry(new_window, textvariable=temp_iquantity)
        iquant_entry.grid(column=1, row=1)
        # Row 3 - measure type
        mtype_label: Label = Label(new_window, text='Measure type')
        mtype_label.grid(column=0, row=2)
        temp_mtype: StringVar = StringVar()
        temp_mtype.set(self.mtype_strvar.get())
        mtype_entry: Entry = Entry(new_window, textvariable=temp_mtype)
        mtype_entry.grid(column=1, row=2)
        # Row 4 - Kroger UPC
        kupc_label: Label = Label(new_window, text='Kroger UPC')
        kupc_label.grid(column=0, row=3)
        temp_kupc: StringVar = StringVar()
        temp_kupc.set(self.kupc_strvar.get())
        kupc_entry: Entry = Entry(new_window, textvariable=temp_kupc)
        kupc_entry.grid(column=1, row=3)
        # Row 5 - Kroger quantity
        kquant_label: Label = Label(new_window, text='Kroger quantity')
        kquant_label.grid(column=0, row=4)
        temp_kquant: DoubleVar = DoubleVar()
        temp_kquant.set(self.kquantity_dvar.get())
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
                   measure_type: str,
                   kroger_upc: str,
                   kroger_quantity: float,
                   new_window: Toplevel):
        # Updates the IngredientDetail control variables from the temp control variables of the edit window.
        self.iname_strvar.set(ingredient_name)
        self.iquantity_dvar.set(ingredient_quantity)
        self.mtype_strvar.set(measure_type)
        self.kupc_strvar.set(kroger_upc)
        self.kquantity_dvar.set(kroger_quantity)

        new_window.destroy()


root = Tk()
idc = IngredientDetailContainer(root)

# detail = IngredientDetail(idc, 1, 'my_ingredient', 3, 'cups', '<No UPC>', 0)
root.mainloop()
