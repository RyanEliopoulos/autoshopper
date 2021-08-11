from tkinter import *
from gui.errormsg import error_message


class NoteFrame(Frame):
    """ Child of the canvas_frame. Holds all widgets associated with the Text widget """

    def __init__(self,
                 parent: 'DetailFrame',
                 recipe_id: int,
                 recipe_notes: str,
                 column: int,
                 row: int):
        self.parent: 'DetailFrame' = parent
        self.recipe_id: int = recipe_id
        Frame.__init__(self, parent)
        self.grid(column=column, row=row)

        # Need save and discard buttons.
        self.btn_frame: Frame = Frame(self)
        self.btn_frame.grid(column=0, row=0)
        self.save_button: Button = Button(self.btn_frame, text='Save', command=self._save_notes)
        self.save_button.grid(column=0, row=0)
        self.discard_button: Button = Button(self.btn_frame, text='Discard changes', command=self._discard_changes)
        self.discard_button.grid(column=1, row=0)
        # Need text widget
        self.text_widget: Text = Text(self)
        self.text_widget.grid(column=0, row=1)
        self.note_string: str = recipe_notes
        self.text_widget.insert('1.0', self.note_string)
        # Registering mousewheel scrolling
        self.bind('<Enter>', lambda evnt: evnt.widget.bind('<MouseWheel>', self.parent.dsf.on_mousewheel))
        self.bind('<Leave>', lambda evnt: evnt.widget.unbind_all('<MouseWheel>'))
        self.btn_frame.bind('<Enter>', lambda evnt: evnt.widget.bind('<MouseWheel>', self.parent.dsf.on_mousewheel))
        self.btn_frame.bind('<Leave>', lambda evnt: evnt.widget.unbind_all('<MouseWheel>'))
        self.save_button.bind('<Enter>', lambda evnt: evnt.widget.bind('<MouseWheel>', self.parent.dsf.on_mousewheel))
        self.save_button.bind('<Leave>', lambda evnt: evnt.widget.unbind_all('<MouseWheel>'))
        self.discard_button.bind('<Enter>', lambda evnt: evnt.widget.bind('<MouseWheel>', self.parent.dsf.on_mousewheel))
        self.discard_button.bind('<Leave>', lambda evnt: evnt.widget.unbind_all('<MouseWheel>'))

    def _save_notes(self):
        """ Pulls the contents of the text widget and sends them to be saved. """
        notes = self.text_widget.get('1.0', END)
        # Save attempt with Model here
        root: 'View' = self.winfo_toplevel()
        note_dict: dict = {'recipe_notes': notes}
        payload: dict = {'change': 'update_notes',
                         'parameter': note_dict}
        ret = root.controller.edit_recipe(self.recipe_id, payload)
        if ret[0] != 0:
            error_message(ret)
        else:
            self.note_string = notes

    def _discard_changes(self):
        """ Changes local to the text widget that will now be reverted """
        self.text_widget.delete('1.0', END)
        self.text_widget.insert('1.0', self.note_string)