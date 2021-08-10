from tkinter import *
from gui.ScrollFrame import ScrollFrame
from gui.SelectFrame import SelectFrame


class SelectionScrollFrame(ScrollFrame):
    """ Formerly RecipesScrollFrame
        Top-level widget controlling the left-hand side of the interface.

        Contains constants for the child widgets. Requires updating the canvas values from
        the inherited class to accommodate these values as the default for the canvas is 1.
    """
    # CONSTANTS for the checkbox+name label containers
    # These are the minsize values.
    select_frame_width = 285
    select_frame_height = 40
    # CONSTANTS for their contents

    def __init__(self, parent, column: int, row: int, recipes: dict, **kwargs):
        ScrollFrame.__init__(self, parent, column, row, **kwargs)
        self.parent: 'View' = parent  # Root
        self.recipes: dict = recipes
        self.framed_recipes = 0  # Track frame count so new recipes can be placed on the bottom.
        # Populating canvas
        self._build_canvas()

    def _build_canvas(self):
        """ Updates the canvas and canvas_frame widgets to suitable size to accommodate the
            incoming select frames.

            Sorts the recipes into alphabetical order before construction.
        """
        self.canvas.configure(width=SelectionScrollFrame.select_frame_width)
        recipe_count = len(self.recipes.keys())
        canvas_scrollregion = recipe_count * SelectionScrollFrame.select_frame_height
        canvas_width = SelectionScrollFrame.select_frame_width
        self.canvas.configure(scrollregion=(0, 0, canvas_width, canvas_scrollregion), width=canvas_width)
        self.canvas_frame.columnconfigure(0, minsize=canvas_width, weight=1)
        # Sorting recipe data alphabetically
        sort_list: list = []
        for key in self.recipes:
            recipe_title = self.recipes[key]['recipe_title']
            sort_list.append((key, recipe_title))
        sort_list.sort(key=lambda x: x[1])
        # Building the frames
        bg = 'light gray'  # Alternating background color for the frames (for contrast)
        for id_name_pair in sort_list:
            recipe_id: int = id_name_pair[0]
            full_recipe: dict = self.recipes[recipe_id]
            SelectFrame(self.canvas_frame,
                        self,
                        SelectionScrollFrame.select_frame_width,
                        SelectionScrollFrame.select_frame_height,
                        full_recipe,
                        self.framed_recipes,
                        bg)
            self.framed_recipes += 1
            if bg == 'light gray':
                bg = 'white'
            else:
                bg = 'light gray'


