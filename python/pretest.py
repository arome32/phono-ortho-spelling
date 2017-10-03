#!/usr/bin/env python

""" This is the main program for the phono-ortho-spelling project.

Structure of the code
=====================

Each different window in the program is implemented as its own class.
For modules that contain logic, such as the Pretest, Training, etc., 
the logic has been decoupled from the visual interface (albeit not
perfectly). 

For example, for the Pretest module, we have three classes:
    PretestModel
    PretestView
    PretestController

The class PretestModel holds the data and the logic, the class 
PretestView represents the visual interface and all its components, and
the PretestController communicates between the two. In an ideal MVC
architecture, the app should be 'skinnable' - it should be possible to 
implement an entirely different look for the app without touching the
core functionality.

A class is a sort of 'blueprint' for creating an object, which can be
thought of as a collection of data and functions. For example, objects
of type 'Noun' (which is a class we have defined in this program) have
attributes such as 'name', 'length', 'img', 'audios', etc. These 
data attributes can be of different types - 'name' is a string,
'length' is an integer, etc.

"""


#from flask import Flask
#app = Flask(__name__)

import os, PIL, random
from os.path import normpath
import pandas as pd
import simpleaudio as sa
from glob import glob
from PIL import Image, ImageTk
import itertools
import typing
from typing import List, Tuple
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import pandas as pd
import time

#==============================================================================
# Some helper functions
#==============================================================================

def play_audio(filepath, wait = False):
    wave_obj = sa.WaveObject.from_wave_file(filepath)
    play_obj = wave_obj.play()
    if wait:
        play_obj.wait_done()


#==============================================================================
# Noun helper class and noun lists
#==============================================================================

class Noun(object):
    def __init__(self, name: str, length: int):
        self.name = name
        self.length = length
        self.img = f"Stimuli/Active/{self.name}/pic_{self.name.lower()}.jpg"
        self.audios = glob(f"Stimuli/Active/{self.name}/*.wav")
        random.shuffle(self.audios)
        self.novel_talker = f"Stimuli/pretest_talker/pretest_talker_{name.lower()}.wav"
        self.production_spelling = None
        self.production_spelling_is_correct = None
        self.perception_spelling = None
        self.variability = None
        self.pretest_correct = None

# List of nouns, divided into short and long nouns

nouns = {}

df = pd.read_csv('word_list.csv', encoding = 'utf-8')

nouns['long'] = df[df['phonemes'] >= 9]['Word'].tolist()
nouns['short'] = df[df['phonemes'] <= 8]['Word'].tolist()

short_nouns = [Noun(name.capitalize(),'short') for name in nouns['short']]
long_nouns = [Noun(name.capitalize(),'long') for name in nouns['long']]

'''
for words in short_nouns:
   print(words.name)

print()

for words in long_nouns:
   print(words.name)


print()
'''

class LoginWindow(ttk.Frame):
    """ This class implements a Login window for the user, where they
    can type in the participant code and the examiner number """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # self.grid(column = 0, row = 0)

        # Define the elements
        title = ttk.Label(self,
                text = "Welcome to the Science Spelling Training", padding = 3)

        # Create text field for entering the participant code
        self.participant_code = tk.StringVar()
        self.participant_code_label = ttk.Label(self,
                text = "Name:", padding = 10)
        self.participant_code_entry = ttk.Entry(self,
                width=20, textvariable = self.participant_code)

        # Create text field for entering the examiner name
        self.login_button = ttk.Button(self, text="Login", command=self.login)

        # Arrange the elements
        title.grid(row = 0, columnspan = 3, pady = 5)
        self.participant_code_label.grid(row=1, column=1, sticky=tk.E, padx= 1)
        self.participant_code_entry.grid(row = 1, column = 2, padx = 1)
        self.login_button.grid(row = 3, column = 2, pady = 10)
        self.controller.bind('<Return>', self.login)
        self.participant_code_entry.focus()

    def login(self, *args):
        self.controller.show_pretest_instructions()
        self.controller.participant_code = self.participant_code_entry.get()

class PretestInstructionsWindow(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent, self.controller = parent, controller

        # Define elements
        with open('pretest_instructions.txt', 'r') as f:
            data = f.read()

        pretest_instructions = ScrolledText(self, borderwidth=10, 
                font = "Helvetica", width=40, wrap = tk.WORD)
            
        pretest_instructions.insert(tk.END, data)
        pretest_instructions.grid()
        self.continue_button = ttk.Button(self, text = "Continue",
                command = self.continue_command, state = 'disabled')
        self.replay_button = ttk.Button(self, text = "Replay test words",
            command = lambda: play_audio("instructions_audio_files/",
                                         "directions_pretest.wav"),
            state = 'disabled')
        self.continue_button.grid()
        self.replay_button.grid()
        self.controller.after(500, self.play_pretest_instructions)

    def play_pretest_instructions(self, *args):
        play_audio("instructions_audio_files/directions_pretest.wav", wait = True)
        self.controller.after(3000, self.enable_continue_button)

    def enable_continue_button(self, *args):
        self.continue_button.config(state='normal')
        self.replay_button.config(state='normal')
        self.controller.bind('<Return>',self.continue_command)

    def continue_command(self, *args):
        self.controller.show_any_questions_window()

class AnyQuestionsWindow(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent, self.controller = parent, controller
        play_audio("instructions_audio_files/directions_anyquestions.wav")
        title = ttk.Label(self, text = "Any questions?")
        title.grid(row = 0, columnspan = 3, pady = 5)
        self.continue_button = ttk.Button(self, text = "Continue",
                command = self.continue_command)
        self.controller.bind('<Return>',self.continue_command)
        self.continue_button.grid()

    def continue_command(self, *args):
        self.controller.start_pretest()

class PretestModel:
    def __init__(self, controller):
        self.count = 0
        self.controller = controller
        self.nouns = self.controller.root.assigned_nouns
        random.shuffle(self.nouns)
        self.nouns = iter(self.nouns) ; self.noun = next(self.nouns)
        self.records, self.n_wrong = {}, 0
        self.dicts = []

    def NextNoun(self, spelling):
        mydict = {  
                    'ORTHO TARGET' : self.noun.name,
                    'PRODUCTION' : spelling,
                    'Length' : self.noun.length,
                    'Condition' : self.noun.variability,
                 }
        self.count +=1
        try:
            if spelling.lower() == self.noun.name.lower():
                mydict['T/F'] = 1
                self.dicts.append(mydict)
                self.noun.pretest_correct = True
                self.noun = next(self.nouns)
            else:
                mydict['T/F'] = 0
                self.dicts.append(mydict)
                self.n_wrong += 1
                self.noun.pretest_correct = False
                #if self.n_wrong == 12:
                #    print('condition met!')
                #    self.controller.do_post_processing()
                #    return
                try: 
                    self.noun = next(self.nouns)
                except StopIteration:
                    try: 
                        self.noun = next(self.nouns)
                    except StopIteration:
                        print(self.count)
                        print('done with iteration!')
                        print(self.dicts)
                        self.controller.do_post_processing()
                        return
        except StopIteration:
            print(self.dicts)
            print('done with iteration!')
            self.controller.do_post_processing()
            return

class PretestView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.EnterButton = ttk.Button(self, text = 'Enter')
        self.EnterButton.grid(row=1, column=1)
        self.SpellingEntry = ttk.Entry(self, width=15, font = "Helvetica 25")
        self.SpellingEntry.grid(row=1, column=0)

    def set_image(self, noun):
        self.noun = noun
        photo = PIL.ImageTk.PhotoImage(PIL.Image.open(self.noun.img))
        self.ImageBox = ttk.Label(self, image = photo)
        self.ImageBox.image=photo
        self.ImageBox.grid(row=0,columnspan=2,
                           padx=10,pady=10,sticky="nsew")

class PretestController:
    def __init__(self, root):
        self.root = root
        self.model = PretestModel(self)
        self.view = PretestView(root.container, self)
        self.view.set_image(self.model.noun)
        self.view.EnterButton.config(command=self.NextImage)
        #self.view.after(3000,self.enable_stuff)
        root.bind('<Return>', self.NextImage)
        self.view.SpellingEntry.focus()
        #self.disable_stuff()
        self.play_noun_audio()

    def NextImage(self, *args):
        #self.view.after(3000,self.enable_stuff)
        spelling = self.view.SpellingEntry.get()
        self.view.SpellingEntry.delete(0, 'end')
        #self.disable_stuff()

        if len(spelling) > 0 and (spelling.isalpha() or " " in spelling):
            self.view.SpellingEntry.delete(0, 'end')
            self.model.NextNoun(spelling)
            if self.model.n_wrong <= 30 and self.model.count !=  30:# or self.model.count <30:
               #self.count +=1
               self.play_noun_audio()
            #print(self.model.noun.name)
            self.view.set_image(self.model.noun)
            self.view.ImageBox.grid(row=0, columnspan=2, padx=10,
                                    pady=10, sticky="nsew")


    def disable_stuff(self):
        self.view.EnterButton.state(["disabled"]) 
        self.view.SpellingEntry.state(["disabled"]) 
        

    def enable_stuff(self):
        self.view.EnterButton.state(["!disabled"]) 
        self.view.SpellingEntry.state(["!disabled"]) 
        
    def do_post_processing(self):
        """ Do post-processing. Does the participant meet the criteria for 
            the study? """
        self.model.results = pd.DataFrame(self.model.dicts,
                columns = ['ORTHO TARGET', 'PRODUCTION','T/F', 'Condition'])
        self.root.filename = 'pretest_'+ self.root.participant_code.replace(" ","_")
        self.root.writer = pd.ExcelWriter(self.root.filename+'.xlsx')
        self.model.results.to_excel(self.root.writer, 'Pretest')

        self.root.writer.save()
        self.root.end_pretest()

    def play_noun_audio(self):
        try:
            audiofile = self.model.noun.novel_talker
            play_audio(audiofile)
        except: 
            pass

class EndPretestWindow(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller

        self.label = ttk.Label(self, text = "Thank you for participating.\nWe will be in touch via email shortly.")
        self.label.grid()


def splitList(xs: List) -> Tuple[List,List]:
    """ Randomly shuffle elements of list into two sublists."""
    random.shuffle(xs)
    length = len(xs)//2
    return xs[:length], xs[length:2*length+1]

def assign_nouns(short_nouns, long_nouns):
    random.shuffle(short_nouns)
    random.shuffle(long_nouns)

    # split the lists into high and low variability sublists
    hi_variability_short, lo_variability_short = splitList(short_nouns)
    hi_variability_long, lo_variability_long = splitList(long_nouns)

    hi_variability = hi_variability_short+hi_variability_long
    lo_variability = lo_variability_short+lo_variability_long

    # Create and set the 'variability' parameter for the noun
    for noun in hi_variability:
        noun.variability = "high"
    for noun in lo_variability:
        noun.variability = "low"

    # Creating an iterator for the combined list of nouns
    assigned_nouns = hi_variability + lo_variability
    random.shuffle(assigned_nouns)
    return assigned_nouns 


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.container = ttk.Frame(self, height = 300, width = 400)
        self.container.grid()
        self.show_login_window()
        self.participant_code = 'default_participant_code'
        self.assigned_nouns = assign_nouns(short_nouns, long_nouns)
        self.writer = None
    def show_login_window(self):
        self.LoginWindow = LoginWindow(self.container, self)
        self.title('Login')
        self.LoginWindow.grid(row = 0, column = 0, sticky = "nsew")
    def show_pretest_instructions(self):
        self.PretestInstructionsWindow=PretestInstructionsWindow(self.container,self)
        self.title('Pretest Instructions')
        self.PretestInstructionsWindow.grid(row = 0, column = 0, sticky = "nsew")
        self.PretestInstructionsWindow.tkraise()
    def show_any_questions_window(self):
        self.AnyQuestionsWindow = AnyQuestionsWindow(self.container, self)
        self.title('Any Questions')
        self.AnyQuestionsWindow.grid(row = 0, column = 0, sticky = "nsew")
        self.AnyQuestionsWindow.tkraise()
    def start_pretest(self):
        self.PretestController = PretestController(self)
        self.title('Pretest')
        self.PretestController.view.grid(row = 0, column = 0, sticky = "nsew")
        self.PretestController.view.tkraise()
    def end_pretest(self):
        self.EndPretestWindow = EndPretestWindow(self.container, self)
        self.EndPretestWindow.grid(row=0,column=0,sticky="nsew")


#@app.route("/")
def main():
    app = MainApplication()
    app.mainloop()
main()
