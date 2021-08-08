from tkinter import *


root = Tk()


mn = Menu(root, title='Title')
root.config(menu=mn)

mn.add_command(label='New Recipe', command=lambda: print("Creating new recipe"))
mn.add_command(label='Delete Recipe', command=lambda: print('Deleting current recipe'))
mn.add_command(label='Load Cart', command=lambda: print('Loading cart'))


root.mainloop()

