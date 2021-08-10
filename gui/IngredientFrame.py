from tkinter import *
from gui.IngredientComponent import IngredientComponent
from gui.errormsg import error_message


class IngredientFrame(Frame):
    """
        Holds the +Ingredient button, plus IngredientComponent objects (Frames) which
        each contain the widgets needed to display the information for a single ingredient entry.
    """

    def __init__(self, parent: Frame, column: int, row: int, recipe: dict):
        """
        :param recipe:  Expects recipe to already be unpacked
        """
        Frame.__init__(self, parent)
        self.grid(column=column, row=row)
        self.parent: Frame = parent
        self.recipe: dict = recipe
        self.ing_button: Button = self._build_button()
        self.ing_index: int = 1  # Relative position tracker for gridding new IngredientComponent objects
        self.ingredient_components: dict = self._build_components()  # Keyed on ingredient_id

    def _build_components(self) -> dict:
        # Iterate through self.recipe['ingredients'] building IngredientComponent objects
        ingredients: dict = self.recipe['ingredients']
        component_dict: dict = {}
        for key in ingredients.keys():
            ingredient_dict: dict = ingredients[key]
            new_component: IngredientComponent = IngredientComponent(self,
                                                                     0,
                                                                     self.ing_index,
                                                                     self.recipe['recipe_id'],
                                                                     ingredient_dict)
            ingredient_id = ingredient_dict['ingredient_id']
            component_dict[ingredient_id] = new_component
            self.ing_index += 1
        return component_dict

    def _build_button(self) -> Button:
        new_button = Button(self, text='+Ingredient', command=self._new_component)
        new_button.grid(column=0, row=0)
        return new_button

    def _new_component(self):
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
        discard_button: Button = Button(new_window, text='Discard', command=lambda: new_window.destroy())
        discard_button.grid(column=1, row=5)
        print("thanks")

    def _save(self,
              recipe_title: str,
              iquant: float,
              mtype: str,
              kupc: str,
              kquant: float,
              new_window: Toplevel):
        """ Saves the newly created ingredient """
        # Requesting ingredient creation through Controller
        ingredient_dict: dict = {'ingredient_name': recipe_title,
                             'ingredient_quantity': iquant,
                             'ingredient_unit_type': mtype,
                             'kroger_upc': kupc,
                             'kroger_quantity': kquant}

        root: 'View' = self.winfo_toplevel()
        ret = root.controller.edit_recipe(self.recipe['recipe_id'], {'change': 'add_ingredient',
                                                           'parameter': ingredient_dict})
        if ret[0] != 0:
            error_message(ret)
        else:
            new_ingredient_id = ret[1]['ingredient_id']
            ingredient_dict['ingredient_id'] = new_ingredient_id
            new_component: IngredientComponent = IngredientComponent(self,
                                                                     0,
                                                                     self.ing_index,
                                                                     self.recipe['recipe_id'],
                                                                     ingredient_dict)
            self.ing_index += 1
            self.ingredient_components[new_ingredient_id] = new_component
        new_window.destroy()


