"""

    How to handle window sizing? Just hardcode values for now and worry about that later.


    columnconfigure(minsize=) Modifies the minimum width
    rowconfigure(minsize=) modifies the minimum height


    Gotta use canvas.create_window in order to get the desired scrolling action.



    Need to add a configure binding to adjust widgets to the root window when it exceeds the minimum dimensions.

"""

from tkinter import *
from tkinter import ttk
from tkinter import messagebox


def print_size(event):
    print(event.widget, event)


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


def clicked_me(event):
    print(f'Clicked {event.widget}')


class RecipesScrollFrame(Frame):
    """
        Frame containing a canvas and a scrollbar for manipulating that canvas, as well as a frame held within
        the canvas as a window.

    """

    def __init__(self, parent, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.parent = parent
        self.active_select_frame = None  # updated by the SelectScreenRecipeFrame objects if they were clicked
        self.grid(column=0, row=0, sticky=(N, S, E, W))
        self.bind('<Button-1>', lambda: print('Clicked me'))
        self.grid_propagate(False)

        # Child canvas
        self.canvas = Canvas(self, height=1000, width=280, scrollregion=(0, 0, 280, 2000))
        self.canvas.grid(column=0, row=0, sticky=(N, S, E, W))
        self.canvas.config(background='green')
        self.canvas.columnconfigure(0, minsize=270)
        self.canvas.rowconfigure(0, minsize=2000)
        self.canvas.grid_propagate(False)

        # Canvas child frame
        self.canvas_frame = Frame(self.canvas, height=1000, width=280)
        canvas_x = self.canvas.canvasx(0)
        canvas_y = self.canvas.canvasy(0)
        self.canvas.create_window((canvas_x, canvas_y), window=self.canvas_frame, anchor='nw')
        self.canvas.bind('<Button-1>', self.canvas_coords)
        #self.select_frame.grid(column=0, row=0, sticky=(N, S, E, W))
        #self.select_frame.grid_propagate(False)
        #self.select_frame.bind('<Button-1>', clicked_me)

        # # # Scrollbar
        scrollbar = Scrollbar(self, width=20)
        scrollbar.grid(column=1, row=0, sticky=(N, S))
        scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=scrollbar.set)



    def canvas_coords(self, event):
        canvasx = event.widget.canvasx(event.x)
        canvasy = event.widget.canvasy(event.y)
        print(f'Clicked ({canvasx}, {canvasy})')

    def build_list(self):
        new_recipe = SelectScreenRecipeFrame(self, self.canvas_frame, "fried chicken", row=0, bg='light gray')
        new_recipe = SelectScreenRecipeFrame(self, self.canvas_frame, "Bacon and eggs", row=1, bg='white')


def clicked_checkbox():
    print("Clicked the checkbox")


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

        self.this.config(background='light blue')
        self.checkbox.config(background='light blue')
        self.label.config(background='light blue')




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

    # Tk begins

    root = Tk()
    root.title('Playing around')
    root.state('zoomed')  # Maximizes window
    rheight = root.winfo_height()
    rwidth = root.winfo_width()

    # left_frame = Frame(root, height=1000, width=1000)
    # left_frame.config(background='red')
    # left_frame.grid(column=0, row=0, sticky=(N, S, E, W))
    left_frame = RecipesScrollFrame(root, height=1000, width=200)
    right_frame = Frame(root, height=1000, width=700)
    right_frame.config(background='blue')
    right_frame.grid(column=1, row=0, sticky=(N, S, E, W))
    #right_frame.lower()

    root.columnconfigure(0, weight=0, minsize=300)
    root.columnconfigure(1, weight=1, minsize=700)
    root.minsize(1000, 1000)

    #root.bind('<Configure>', print_size)
    root.bind('f', on_demand)

    def frame_resize(the_root, the_left_frame, the_right_frame):
        left_height = the_root.winfo_height()
        #left_width = int(the_root.winfo_width() * .8)

        right_height = left_height
        #right_width = int(the_root.winfo_width() * .2)

        the_left_frame.config(height=left_height)
                              #width=left_width)
        the_left_frame.build_list()

        the_right_frame.config(height=right_height)
                              #width=right_width)

    root.after(1, frame_resize, root, left_frame, right_frame)
    root.mainloop()