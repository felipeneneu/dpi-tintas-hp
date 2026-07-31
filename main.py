import sys
import os
import tkinter.font as tkfont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.theme import get_font_path
import customtkinter as ctk
from controllers.main_controller import MainController


def load_fonts():
    tkfont.Font(file=get_font_path("Poppins-Bold"), family="Poppins", size=16, weight="bold")
    tkfont.Font(file=get_font_path("Poppins-Medium"), family="Poppins", size=13)
    tkfont.Font(file=get_font_path("OpenSans-Regular"), family="Open Sans", size=11)


def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    load_fonts()

    app = MainController()
    app.executar()


if __name__ == "__main__":
    main()
