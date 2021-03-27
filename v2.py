"""

    How to handle window sizing? Just hardcode values for now and worry about that later.


    columnconfigure(minsize=) Modifies the minimum width
    rowconfigure(minsize=) modifies the minimum height


    Gotta use canvas.create_window in order to get the desired scrolling action.



    Need to add a configure binding to adjust widgets to the root window when it exceeds the minimum dimensions.



    Need to address widget sizing. Should rewrite what I've got to be cleaner.


"""

from tkinter import *
from tkinter import ttk
from tkinter import messagebox


class ScrollFrame(Frame):
    """
        Frame containing a canvas and a scrollbar for manipulating that canvas, as well as a frame held within
        the canvas as a window.

        Sizing is hardcoded. Should probably be based on CONSTANTS or something
    """
    def __init__(self, column, row, parent, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.parent = parent
        self.grid(column=column, row=row, sticky=(N, S, E, W))
        self.grid_propagate(False)

        # Setting up mouse wheel functionality
        # self.bind('<Enter>', self._bound_to_mousewheel)
        # self.bind('<Leave>', self._unbound_to_mousewheel)

        # Child canvas
        self.canvas = Canvas(self, height=1000, width=280, scrollregion=(0, 0, 280, 2000))
        self.canvas.grid(column=0, row=0, sticky=(N, S, E, W))
        # self.canvas.config(background='green')
        # self.canvas.columnconfigure(0, minsize=270)
        # self.canvas.rowconfigure(0, minsize=2000)
        self.canvas.grid_propagate(False)
        self.canvas.bind('<Button-1>', self.hide)

        # Canvas child frame
        self.canvas_frame = Frame(self.canvas, height=1000, width=280)
        canvas_x = self.canvas.canvasx(0)
        canvas_y = self.canvas.canvasy(0)
        self.ret_val = self.canvas.create_window((canvas_x, canvas_y), window=self.canvas_frame, anchor='nw')
        self.frame_hidden = False

        # self.canvas_frame.bind('<Enter>', self._bound_to_mousewheel)
        # self.canvas_frame.bind('<Leave>', self._unbound_to_mousewheel)
        # # # Scrollbar
        scrollbar = Scrollbar(self, width=20)
        scrollbar.grid(column=1, row=0, sticky=(N, S))
        scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=scrollbar.set)

    def _bound_to_mousewheel(self, event):
        print('bound')
        self.canvas_frame.bind('<MouseWheel>', self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        print('unbound')
        self.canvas_frame.unbind_all('<MouseWheel>')

    def _on_mousewheel(self, event):
        #print('here')
        self.canvas.yview_scroll(int(-1*(event.delta/120)), 'units')



    def hide(self, event):
        print('in hide')
        if self.frame_hidden:
            self.frame_hidden = False
            self.canvas.itemconfig(self.ret_val, state='normal')
        else:
            self.frame_hidden = True
            self.canvas.itemconfig(self.ret_val, state='hidden')


class SelectMenu:

    def __init__(self, root_widget, recipes: list[dict]):
        self.root_widget = root_widget
        self.recipes: list[dict] = recipes  # I think I want this key/value keyed on recipe name

        # Left side frame
        self.recipes_scrollframe = RecipesScrollFrame(recipes, 0, 0, root_widget, height=1000, width=200)
        # Right side frame
        self.recipe_displayframe = DisplayScrollFrame(recipes, 1, 0, root_widget, height=1000, width=700)
        # Setting one-way communication method (left side frame -> right side frame)
        self.recipes_scrollframe.displayrecipe = self.recipe_displayframe.makevisible
        # self.right_frame = Frame(root_widget, height=1000, width=700)
        # self.right_frame.config(background='blue')
        # self.right_frame.grid(column=1, row=0, sticky=(N, S, E, W))


        # Root widget settings
        self.root_widget.columnconfigure(0, weight=0, minsize=300)
        self.root_widget.columnconfigure(1, weight=1, minsize=700)
        self.root_widget.minsize(1000, 800)
        self.root_widget.after(1, self.frame_resize)

    def update_displayed_recipe(self ):
        ...

    def frame_resize(self):
        left_height = self.root_widget.winfo_height()
        #left_width = int(the_root.winfo_width() * .8)

        right_height = left_height
        #right_width = int(the_root.winfo_width() * .2)

        self.recipes_scrollframe.config(height=left_height)
                              #width=left_width)
        self.recipes_scrollframe.build_list()

        self.recipe_displayframe.config(height=right_height)
                              #width=right_width)
        self.recipe_displayframe.build_list()


class RecipesScrollFrame(ScrollFrame):
    """
        Frame containing a canvas and a scrollbar for manipulating that canvas, as well as a frame held within
        the canvas as a window.

    """

    def __init__(self, recipes: list[dict], column, row, parent, **kwargs):
        ScrollFrame.__init__(self, column, row, parent, **kwargs)
        self.parent = parent
        self.recipes = recipes
        self.active_select_frame = None
        self.displayrecipe = None  # A method to communicate with the right frame. Is updated by SelectMenu.

        self.canvas.config(background='green')
        self.canvas.columnconfigure(0, minsize=270)
        self.canvas.rowconfigure(0, minsize=2000)

    def build_list(self):
        bg = 'light gray'
        for index, recipe in enumerate(self.recipes):
            SelectScreenRecipeFrame(self, self.canvas_frame, recipe['name'], row=index, bg=bg)
            if bg == 'light gray':
                bg = 'white'
            else:
                bg = 'light gray'


class SelectScreenRecipeFrame:

    """
        Will contain a checkbox indicating recipe selection status
        and a label providing the recipe name
    """

    def __init__(self, recipe_scrollframe, parent_frame, recipe_name, row, bg):
        # This object
        self.recipe_scrollframe = recipe_scrollframe
        self.parent_frame = parent_frame
        self.default_color = bg
        self.recipe_name = recipe_name

        # Frame
        self.this = Frame(parent_frame, height=40, width=285)
        self.this.columnconfigure(0, minsize=20)
        self.this.columnconfigure(1, minsize=20)
        self.this.grid(column=0, row=row, sticky=W)
        self.this.config(background=bg)
        self.this.grid_propagate(False)
        # Checkbox
        self.checkbox_var = IntVar()
        # Height seems to move the widget up/down within the parent. Width moves right to left
        self.checkbox = Checkbutton(self.this, variable=self.checkbox_var, command=lambda: print('clicked'), height=2)
        self.checkbox.grid(column=0, row=0)
        self.checkbox.config(background=bg)
        # Label
        self.label = Label(self.this, text=recipe_name)
        self.label.grid(column=1, row=0)
        self.label.config(background=bg)

        # Binding mouse click 1 to highlight action
        self.this.bind('<Button-1>', self.select_recipe_frame)
        self.label.bind('<Button-1>', self.select_recipe_frame)

        # Binding mousewheel to scrolling (I hope)
        # Recipe Frame
        self.this.bind('<Enter>', self._bound_to_mousewheel)
        self.this.bind('<Leave>', self._unbound_to_mousewheel)
        # checkbox
        self.checkbox.bind('<Enter>', self._bound_to_mousewheel)
        self.checkbox.bind('<Leave>', self._unbound_to_mousewheel)
        # label
        self.label.bind('<Enter>', self._bound_to_mousewheel)
        self.label.bind('<Leave>', self._unbound_to_mousewheel)

    def default_colors(self):
        self.this.config(background=self.default_color)
        self.checkbox.config(background=self.default_color)
        self.label.config(background=self.default_color)
        print("In default colors")

    def select_recipe_frame(self, event):
        """
            This should be bound to mouse1 for the select frames and their children

            Changes the background color to indicate selected.  Informs select frame of the new selection so it
            can toggle off the old selected recipe frame.
        """
        old_recipe_frame = self.recipe_scrollframe.active_select_frame
        if old_recipe_frame is not None:
            old_recipe_frame.default_colors()

        self.recipe_scrollframe.active_select_frame = self
        self.recipe_scrollframe.displayrecipe(self.recipe_name)

        self.this.config(background='light blue')
        self.checkbox.config(background='light blue')
        self.label.config(background='light blue')

    def _bound_to_mousewheel(self, event):
        print('bound')
        event.widget.bind('<MouseWheel>', self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        print('unbound')
        event.widget.unbind_all('<MouseWheel>')

    def _on_mousewheel(self, event):
        print('here')
        self.recipe_scrollframe.canvas.yview_scroll(int(-1*(event.delta/120)), 'units')

class DisplayScrollFrame(ScrollFrame):
    """
        Presents the right-hand side of the selection screen. Displays the recipe information
        of the recipe currently highlighted on the left side of the screen.
    """

    def __init__(self, recipes: list[dict], column, row, parent, **kwargs):
        ScrollFrame.__init__(self, column, row, parent, **kwargs)
        self.recipes = recipes
        self.display_frames: dict = {}
        self.displayedframe = None
        # Has a dict of the recipe display frames keyed to recipe name?
        self.columnconfigure(0, minsize=680)
        self.columnconfigure(1, minsize=20)
        super().config(background='blue')

    def build_list(self):
        """
            Builds out the frames that display the recipe information.
        :return:
        """
        ...
        for recipe in self.recipes:
            new_frame = SelectScreenRecipeDisplayFrame(recipe, self.canvas_frame, height=1000, width=700)
            recipe_name = recipe['name']
            self.display_frames[recipe_name] = new_frame

    def makevisible(self, recipe_name: str):
        if self.displayedframe is not None:
            self.displayedframe.grid_remove()
        self.displayedframe = self.display_frames[recipe_name]
        self.displayedframe.grid()


class SelectScreenRecipeDisplayFrame(Frame):
    """
        This object displays all the information about a given recipe.
    """

    def __init__(self, recipe: dict, parent, **kwargs):
        # Attending to self
        Frame.__init__(self, parent, **kwargs)
        self.grid(column=0, row=0)
        # Recipe name label
        self.recipe_label = Label(self, height=100, width=100, text=recipe['name'], anchor='nw', font=('', 30))
        self.recipe_label.grid(column=0, row=0)
        # "Ingredient" header
        self.ingredient_header = Label(self, height=100, width=100, text='Ingredients', anchor='nw')
        self.ingredient_header.grid(column=0, row=1)

        self.grid_remove()  # Frame is hidden unless the recipe is been clicked


if __name__ == "__main__":

    first_recipe = {
        'name': 'tacos',
        'ingredients': [
            {'ingredient_name': 'ground beef',
             'quantity': 1},
            {'ingredient_name': 'taco shell',
             'quantity': 1}
        ],
        'notes': 'This is the long list of words and letters\nThat ultimately will make up the note zone'
    }

    second_recipe = {
        'name': 'spaghetti',
        'ingredients': [
            {'ingredient_name': 'noodles',
             'quantity': 1},
            {'ingredient_name': 'sauce',
             'quantity': 1}
        ],
        'notes': 'I like noodles'
    }

    third_recipe = {
        'name': 'toast',
        'ingredients': [
            {'ingredient_name': 'bread',
             'quantity': 1},
            {'ingredient_name': 'butter',
             'quantity': 1}
        ],
        'notes': 'I like toast even more'
    }

    recipes = [first_recipe, second_recipe, third_recipe]
    recipes.sort(key=lambda recipe: recipe['name'])
    root = Tk()
    root.title('Playing around')
    root.state('zoomed')  # Maximizes window

    def on_demand(event):

        """
            Prints size of the widget that was clicked
        :param event:
        :return:
        """
        widget_height = event.widget.winfo_height()
        widget_width = event.widget.winfo_width()
        print(f'Size of {event.widget}: ({widget_height}, {widget_width})')

        children = event.widget.winfo_children()

        def recurse(child):
            height = child.winfo_height()
            width = child.winfo_width()
            print(f'Size of {child}: ({height}, {width})')

            grandchildren = child.winfo_children()
            for grandchild in grandchildren:
                recurse(grandchild)

        for child in children:
            recurse(child)
    root.bind('f', on_demand)

    select_menu = SelectMenu(root, recipes)

    root.mainloop()