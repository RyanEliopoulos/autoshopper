from tkinter import *


def error_message(message: str):
    """ Just relays a popup conveing a message and dismiss button """
    new_window: Toplevel = Toplevel(width=400, height=400)
    msg_label: Label = Label(new_window, text=message)
    msg_label.grid(column=0, row=0)
    dismiss_btn: Button = Button(new_window,
                                 text='OK',
                                 command=lambda: new_window.destroy())
    dismiss_btn.grid(column=0, row=1)
