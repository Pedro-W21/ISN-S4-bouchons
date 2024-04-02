from interface import App

class Creation_Route:

    def __init__(self):
        self.app = App()
        width, height = App().carte.winfo_width(), App().carte.winfo_height()
        print(width, height)


Creation_Route()