from tkinter import *


class ScrollFrame(Frame):
    """ Frame containing a canvas and a scrollbar for manipulating that canvas, as well as a frame held within
        the canvas as a window.

        ScrollFrame adjusts to fit contents (the Canvas) as well as the frame held within the canvas,
        but the canvas itself must be manually adjusted.

        Additionally, the Canvas is initialized with width, height, and scroll region values of zero.

        Scrollbar values ARE hardcoded.

    """

    def __init__(self, parent, column, row, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.parent = parent
        self.grid(column=column, row=row, sticky=(N, S, E, W))
        self.columnconfigure(0, weight=1)  # Allows canvas to match Frame resize horizontally
        self.rowconfigure(0, weight=1)  # Ditto vertically  #@TODO A canvas larger than the list scrolls erroneously
        self.config(background='yellow')
        self.propagate(False)
        # Child canvas
        self.canvas = Canvas(self, height=1, width=1, scrollregion=(0, 0, 0, 0))
        self.canvas.grid(column=0, row=0, sticky=(N, S, E, W))
        self.canvas.config(background='green')
        self.canvas.columnconfigure(0, minsize=1)
        self.canvas.rowconfigure(0, minsize=1)
        self.canvas.grid_propagate(False)  # Must be manually resized
        self.canvas.bind('<Enter>', self._bind_scroll_fnx)  # Enabling <MousewWheel> scrolling
        self.canvas.bind('<Leave>', self._unbind_scroll_fnx)  # Disabling scrolling for the region upon departure
        # Canvas child frame
        self.canvas_frame = Frame(self.canvas, height=1, width=1)
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.config(background='orange')
        self.canvas_frame.propagate(False)
        canvas_x = self.canvas.canvasx(0)
        canvas_y = self.canvas.canvasy(0)
        self.canvas.create_window((canvas_x, canvas_y), window=self.canvas_frame, anchor=N+W)
        self.canvas_frame.bind('<Enter>', self._bind_scroll_fnx)
        self.canvas_frame.bind('<Leave>', self._unbind_scroll_fnx)
        # Scroll bar
        scrollbar = Scrollbar(self, width=20)
        scrollbar.grid(column=1, row=0, sticky=(N, S))
        scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=scrollbar.set)
        # Padding for the sake of menu button visibility
        self.config(pady=5)

    def _bind_scroll_fnx(self, event):
        """ Activates scrolling functionality to the given widgets when mouse is present """
        print('bound')
        event.widget.bind('<MouseWheel>', self.on_mousewheel)

    def _unbind_scroll_fnx(self, event):
        """ Deactivated scrolling functionality when the mouse is no longer present """
        print('unbound')
        event.widget.unbind('<MouseWheel>')

    def on_mousewheel(self, event):
        print('Mouse scrolling activated')

        # Enforce sanity check for scrolling here?
        canvas_height: int = self.canvas.winfo_height()
        region_str: str = self.canvas.cget('scrollregion')
        scrollregion_height = int(region_str.split(' ')[3])
        if scrollregion_height > canvas_height:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')




