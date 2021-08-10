from tkinter import *
from gui.ScrollFrame import ScrollFrame
from gui.DetailFrame import DetailFrame


class DetailScrollFrame(ScrollFrame):

    def __init__(self, parent: Tk, column: int, row: int, recipes: dict, **kwargs):
        ScrollFrame.__init__(self, parent, column, row, **kwargs)
        self.detail_frames: dict = self._build_detail_frames(recipes)
        self.visible_frame = None  # The active DetailFrame

    def _build_detail_frames(self, recipes: dict) -> dict:
        """ Returns a dict whose {K,V} are recipe_id and detail frames. """
        frame_dict: dict = {}
        for recipe_id in recipes.keys():
            recipe: dict = recipes[recipe_id]
            new_detailframe = DetailFrame(self, recipe)
            frame_dict[recipe_id] = new_detailframe
        return frame_dict

    def make_visible(self, recipe_id):
        if self.visible_frame is not None:
            # Turn off
            self.visible_frame.toggle_visibility()
        # Turn on
        self.visible_frame = self.detail_frames[recipe_id]
        self.visible_frame.toggle_visibility()



