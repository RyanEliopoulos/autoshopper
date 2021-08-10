from tkinter import *


class SelectFrame(Frame):
    """ Provides a label for recipe name and a checkbox indicating selected status.
        Contained within the canvas_frame, itself belonging to the ScrollFrame
    """

    def __init__(self,
                 parent: Frame,
                 ssf: 'SelectionScrollFrame',
                 width: int,
                 height: int,
                 recipe: dict,
                 row: int,
                 bg: str):
        Frame.__init__(self, parent, width=width, height=height)
        self.parent: SelectionScrollFrame = parent
        self.ssf = ssf
        self.recipe_id: int = recipe['recipe_id']
        self.default_color: str = bg
        self.grid(column=0, row=row, sticky=(N, S, E, W))  # Sticky ensures full sizing Perhaps "weight" in the parent would do as well
        self.propagate(False)
        self.configure(background='blue')
        # Establishing norms for contained widgets
        self.columnconfigure(0, minsize=20)
        self.columnconfigure(1, minsize=20, weight=1)  # weight allows the label to stretch!

        # Building contents
        self.checkbox_var: IntVar = IntVar()
        self.checkbox: Checkbutton = Checkbutton(self, height=2, variable=self.checkbox_var)
        self.checkbox.grid(column=0, row=0)
        self.checkbox.config(background=bg)
        # # # Label
        self.label: Label = Label(self, width=1, height=1, text=recipe['recipe_title'])
        self.label.grid(column=1, row=0, sticky=(N, S, E, W))
        self.label.config(background=bg)

        # Enabling scrolling action
        self.bind('<Enter>', lambda evnt: evnt.widget.bind('<MouseWheel>', self.ssf.on_mousewheel))
        self.bind('<Leave>', lambda evnt: evnt.widget.unbind_all('<MouseWheel>'))
        self.checkbox.bind('<Enter>', lambda evnt: evnt.widget.bind('<MouseWheel>', self.ssf.on_mousewheel))
        self.checkbox.bind('<Leave>', lambda evnt: evnt.widget.unbind_all('<MouseWheel>'))
        self.label.bind('<Enter>', lambda evnt: evnt.widget.bind('<MouseWheel>', self.ssf.on_mousewheel))
        self.label.bind('<Leave>', lambda evnt: evnt.widget.unbind_all('<MouseWheel>'))

    def default_color(self):
        """ Resets the frame to its default color. Invoked when the frame is deselected. """
        self.config(background=self.default_color)
        self.checkbox.config(background=self.default_color)
        self.label.config(background=self.default_color)
