#!/usr/bin/env python
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import simpleaudio as sa
from glob import glob
from PIL import Image, ImageTk
import random
import os

# from Session import Session

def play_audio(filepath):
    wave_obj = sa.WaveObject.from_wave_file(filepath)
    wave_obj.play()

class Noun(object):
    def __init__(self, name):
        self.name = name
        self.imgs = glob("Nouns/{}/*.jpg".format(self.name))
        # self.imagecollection = os.listdir(imgs_path)

class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        container = ttk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for f in (Login, Instructions, Pretest, end_pretest):
            name = f.__name__
            frame = f(container, self)
            self.frames[name] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame("Login")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class end_pretest(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid()
        label = ttk.Label(self, text = "Pretest done")
        label.grid()

class Pretest(ttk.Frame):
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid()
        self.nouns = [Noun(name) for name in os.listdir("Nouns")]
        self.pairs = [(self.nouns[i], self.nouns[i+1]) for i in range(0, 18, 2)]

        spelling = tk.StringVar()
        spelling_entry = ttk.Entry(self, width=20, textvariable = spelling)
        spelling_label = ttk.Label(self, text = "Type word here")
        spelling_label.grid(row = 1, column = 0)
        spelling_entry.grid(row = 1, column = 1)

        random.shuffle(self.pairs)
        
        # Enter button
        gen = self.noun_generator()

        self.noun = next(gen)
        print(self.noun.name)
        self.show_pretest_image(self.noun)
        spelling_entry.focus()

        def enter(sp):
            if sp == self.noun.name: 
                print('ok') 
            else: print('not ok')
            self.noun = next(gen)
            print(self.noun.name)
            self.show_pretest_image(self.noun)
            # Clear the field
            spelling_entry.delete(0, 'end')

        enter_button = ttk.Button(self, text = "Enter",
                command = lambda: enter(spelling_entry.get()))
        enter_button.grid(row = 2, column = 1)
        self.controller.bind('<Return>', lambda x: enter(spelling_entry.get()))

    # choose a word pair randomly
    def noun_generator(self):
        for pair in self.pairs:
            yield random.choice(pair)

    def show_pretest_image(self, randomnoun):
        randomimage = random.choice(randomnoun.imgs)

        # Image appears
        image = Image.open(randomimage)
        photo = ImageTk.PhotoImage(image)
        image_label = ttk.Label(self, image = photo)
        image_label.image = photo
        image_label.grid(row = 0, columnspan=2, padx = 10, pady = 10, sticky = "nsew")

    # def run_pretest(self, spelling_entry): 
    #     n = 0
    #     spelling = spelling_entry.get()
    #     print(spelling)
    #     if spelling != "" and spelling == randomnoun.name:
    #         print('correcto!')
    #     else:
    #         print('wrong!')
    #         yield
    #             else:
    #             print('done2')
    #             self.controller.show_frame("end_pretest")




            
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
        replay_button = ttk.Button(self, text = "Replay test words",
                command = lambda: play_audio("instructions.wav"))

        # Arrange elements
        replay_button.grid()

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


if __name__=="__main__":
    app = MainApplication()
    app.mainloop()
