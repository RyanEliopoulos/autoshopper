from tkinter import *






# class NoteFrame(Frame):
#
#     def __init__(self, parent):
#         Frame.__init__(self, parent)
#         self.grid(column=0, row=0)
#         self.text_widget: Text = Text(self)
#         self.text_widget.grid(column=0, row=1)
#
#         self.print_button: Button = Button(self, text='print_info', command=self._print_info)
#         self.print_button.grid(column=0, row=0)
#
#         self.insert_button: Button = Button(self, text='insert text', command=self._insert_text)
#         self.insert_button.grid(column=1, row=0)
#
#         self.delete_button: Button = Button(self, text='delete button', command=self._delete_text)
#         self.delete_button.grid(column=2, row=0)
#         """
#         Guess I create a save and discard button. Discard will repopoulate the text widget with
#         the notes. Save makes the current contents of the widget canonical.
#         """
#
#     def _print_info(self):
#         print(self.text_widget.get('1.0', END))
#
#     def _insert_text(self):
#         desired_text = 'HELLO THERE KENOBI'
#         self.text_widget.insert('0.0', desired_text)
#
#     def _delete_text(self):
#         self.text_widget.delete('1.0', END)
class NoteFrame(Frame):
    """" Interface for text widget, enabling user management of recipe notes. """

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.grid(column=0, row=0)
        self.text_widget: Text = Text(self)
        self.text_widget.grid(column=0, row=1)
        self.note_string: str = ''

        self.save_button: Button = Button(self, text='save', command=self._save_notes)
        self.save_button.grid(column=0, row=0)
        self.discard_button: Button = Button(self, text='discard changes', command=self._discard_changes)
        self.discard_button.grid(column=1, row=0)

    def _save_notes(self):
        notes = self.text_widget.get('1.0', END)
        # Save attempt with Model here
        # New window confirming successful saving
        self.note_string = notes
        print(f'saved notes: {self.note_string}')

    def _discard_changes(self):
        """ Changes local to the text widget that will now be reverted """
        self.text_widget.delete('1.0', END)
        self.text_widget.insert('1.0', self.note_string)



root = Tk()

nf = NoteFrame(root)
root.mainloop()