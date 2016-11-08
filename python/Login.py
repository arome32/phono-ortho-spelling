import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import simpleaudio as sa
from PIL import Image, ImageTk
import random
from glob import glob
import os
from helpers import play_audio

class Login(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        style = ttk.Style()
        style.configure("Label", foreground = "black", background = "white")
        style.configure("Button", foreground = "black", background = "white")
        self.grid(column = 0, row = 0)

        # Define the elements
        title = ttk.Label(self, text = "Word Trainer") 
       
        participant_code = tk.StringVar()
        participant_code_label = ttk.Label(self, text = "Participant Code:", style = "Label")
        participant_code_entry = ttk.Entry(self, width=20, textvariable = participant_code)

        examiner = tk.StringVar()
        examiner_entry = ttk.Entry(self, width=20, textvariable = examiner)
        examiner_label = ttk.Label(self, text = "Examiner:", style = "Label")
        
        def login():
            controller.show_frame("Instructions")
            play_audio("instructions.wav")
            play_audio("instructions.wav")

        login_button = ttk.Button(self, text = "Login", command = login)
                

        # Arrange the elements
        title.grid(row = 0, columnspan=3, pady = 5)
        participant_code_label.grid(row = 1, column = 1, sticky=tk.E, padx = 1)
        participant_code_entry.grid(row = 1, column = 2, padx = 1)
        examiner_label.grid(row = 2, column = 1,sticky = tk.E, padx = 1)
        examiner_entry.grid(row = 2, column = 2, padx = 1)
        login_button.grid(row = 3, column = 2, pady = 10)
        participant_code_entry.focus()

