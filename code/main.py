import os
from interface.interface import App
from os.path import abspath, dirname

if __name__ == "__main__":
    os.chdir(dirname(abspath(__file__)))

    app = App()
    app.mainloop()
