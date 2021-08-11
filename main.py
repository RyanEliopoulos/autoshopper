import Controller
import gui.View as View

if __name__ == "__main__":
    db_path = './test.db'
    controller = Controller.Controller(db_path)
    vw = View.View(controller)
    # vw.mainloop()