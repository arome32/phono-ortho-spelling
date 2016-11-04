#!/usr/bin/env python
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import simpleaudio as sa
from PIL import Image, ImageTk

# from Session import Session

def play_audio(filepath):
    wave_obj = sa.WaveObject.from_wave_file(filepath)
    wave_obj.play()

class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        container = ttk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for f in (Login, Instructions, Pretest):
            name = f.__name__
            frame = f(container, self)
            self.frames[name] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame("Login")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class Pretest(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid()

        # Define elements
        # choose a word pair randomly
        # Image appears
        image = Image.open("Osteoclast_Good_6.png")
        photo = ImageTk.PhotoImage(image)
        l = ttk.Label(self, image = photo)
        l.image = photo
        l.grid(row = 0, columnspan=2)
        spelling = tk.StringVar()
        spelling_entry = ttk.Entry(self, width=20, textvariable = spelling)
        spelling_label = ttk.Label(self, text = "Type word here")
        spelling_label.grid(row = 1, column = 0)
        spelling_entry.grid(row = 1, column = 1)
        # play_audio(word_filepath)
        # randomly choose a member of the pair
        # textbox appears
        # Enter button
    # command to execute when enter is clicked
        # if participant misspells word:
            # test them with next word in set

class Instructions(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Define elements
        with open('instructions.txt', 'r') as f:
            data = f.read()
        instructions = ScrolledText(self, borderwidth=10, font = "Helvetica", 
                                width=40, wrap = tk.WORD)
        instructions.insert(tk.END, data)
        instructions.grid()

        continue_button = ttk.Button(self, text = "Continue",
                command = lambda: controller.show_frame("Pretest"))
        continue_button.grid()
        # replay_button = ttk.Button(self, text = "Replay test words",
                                   # command = play_audio(test_words))

        # Arrange elements
        # replay_button.grid()

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

        login_button = ttk.Button(self, text = "Login", command = login)
                

        # Arrange the elements
        title.grid(row = 0, columnspan=3, pady = 5)
        participant_code_label.grid(row = 1, column = 1, sticky=tk.E, padx = 1)
        participant_code_entry.grid(row = 1, column = 2, padx = 1)
        examiner_label.grid(row = 2, column = 1,sticky = tk.E, padx = 1)
        examiner_entry.grid(row = 2, column = 2, padx = 1)
        login_button.grid(row = 3, column = 2, pady = 10)
        participant_code_entry.focus()


if __name__=="__main__":
    app = MainApplication()
    app.mainloop()
