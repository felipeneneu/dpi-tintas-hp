import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from controllers.main_controller import MainController


def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = MainController()
    app.executar()


if __name__ == "__main__":
    main()
