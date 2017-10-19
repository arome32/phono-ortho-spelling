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

import xlrd
import csv
import os, PIL, random
from random import randint
from os.path import normpath
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import simpleaudio as sa
from glob import glob
from PIL import Image, ImageTk
import itertools
from tkinter import filedialog
import typing
from typing import List, Tuple
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import pandas as pd
import time


input_file = None
dicts = []
var = None

to_output = []


#==============================================================================
# Some helper functions
#==============================================================================
def play_audio(filepath, wait = False):
    wave_obj = sa.WaveObject.from_wave_file(filepath)
    play_obj = wave_obj.play()
    if wait:
        play_obj.wait_done()


def open_file():
   global input_file
   root = tk.Tk()
   root.withdraw()

   file_path = filedialog.askopenfilename()
   return file_path

def csv_from_excel(path):
    wb = xlrd.open_workbook(path)
    sh = wb.sheet_by_name('Pretest')
    your_csv_file = open('pretest.csv', 'w')
    wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

    for rownum in range(sh.nrows):
        wr.writerow(sh.row_values(rownum))

    your_csv_file.close()


def load_everything_in():
    for i in range(1, len(input_file)):
       if input_file[i].strip() == "":
          continue
          
       line = input_file[i].strip()

       line = line.split(",")[1:]
       
       tf = int(line[2].replace('.0','').replace('"',''))
       
       toAdd = {
                  'Word' : line[0].replace('"',""),
                  'Participant Answer' : line[1].replace('"',""),
                  'T/F' : tf,
                  'Condition' : line[3].replace('"',"")
               }
       dicts.append(toAdd)
       #print(toAdd)


def pick_12():
    global dicts
    to_do = dicts
    new_dicts = []
    i = 0
    num = 5

    while i < num:
        print("i ",i)
        num = randint(0,len(dicts)-1)
        if(dicts[num] in new_dicts):
            print("one")
            continue
        else:
            print("two")
            new_dicts.append(dicts[num]) 
            i += 1
    #for word in new_dicts:
    #    print(word)
    dicts =  new_dicts
    
def use_pretest_nouns(nouns): 
    new_nouns = []
    print(len(dicts))

    for word in dicts:
        print(word)
        for noun in nouns:
           if word["Word"] == noun.name:
               noun.pretest_correct = False
               noun.production_spelling = word["Participant Answer"]
               new_nouns.append(noun)
               break
    return new_nouns
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
    
    def __str__(self):
        return self.name + " " + str(self.length) + " " + str(self.production_spelling) + " " + str(self.perception_spelling)

# List of nouns, divided into short and long nouns

nouns = {}

df = pd.read_csv('word_list.csv', encoding = 'utf-8')

nouns['long'] = df[df['phonemes'] >= 9]['Word'].tolist()
nouns['short'] = df[df['phonemes'] <= 8]['Word'].tolist()

short_nouns = [Noun(name.capitalize(),'short') for name in nouns['short']]
long_nouns = [Noun(name.capitalize(),'long') for name in nouns['long']]


class LoginWindow(ttk.Frame):
    """ This class implements a Login window for the user, where they
    can type in the participant code and the examiner number """
    def __init__(self, parent, controller):
        global input_file
        
        self.ready = False
        self.incorrect_file = False

        super().__init__(parent)
        self.controller = controller
        # self.grid(column = 0, row = 0)

        # Define the elements
        title = ttk.Label(self,
                text = "Welcome to the Science Spelling Training", padding = 3)

        # Create text field for entering the participant code
        self.participant_code = tk.StringVar()
        self.participant_code_label = ttk.Label(self,
                text = "Participant Code:", padding = 10)
        self.participant_code_entry = ttk.Entry(self,
                width=20, textvariable = self.participant_code)

        # Create text field for entering the examiner name
        self.examiner = tk.StringVar()
        self.examiner_entry = ttk.Entry(self, width=20,
                textvariable = self.examiner)
        self.examiner_label = ttk.Label(self, text="Examiner:", padding = 10)
        
        self.login_button = ttk.Button(self, text="Login", command=self.login)
        
        self.load_button = ttk.Button(self, text="Load Pretest Data", command=self.load)
        self.load_label = ttk.Label(self, text="", padding = 10)

        # Arrange the elements
        title.grid(row = 0, columnspan = 3, pady = 5)
        
        self.participant_code_label.grid(row=1, column=1, sticky=tk.E, padx= 1)
        self.participant_code_entry.grid(row = 1, column = 2, padx = 1)

        self.examiner_label.grid(row = 2, column = 1,sticky = tk.E, padx = 1)
        self.examiner_entry.grid(row = 2, column = 2, padx = 1)

        self.login_button.grid(row = 3, column = 2, pady = 10)
        self.load_button.grid(row = 3, column = 1, pady = 10)
        self.load_label.grid(row = 4, column = 1, pady = 10)

        self.controller.bind('<Return>', self.login)
        self.participant_code_entry.focus()

    def login(self, *args):
        if(self.ready):
            self.controller.show_training_instructions()
            self.controller.participant_code = self.participant_code_entry.get()
            self.controller.examiner = self.examiner_entry.get()
        else:
            if(not self.incorrect_file):
                self.load_label['text'] = 'Please select a file'
            
    def load(self, *args):
        global input_file
        to_Open = str(open_file())
        file_name = to_Open.split("/")[-1]
        if(to_Open == '()' or to_Open == ""):
            self.load_label['text'] = 'Please select a file'
        else:
            if(".xlsx" in to_Open):
                self.ready = True
                self.incorrect_file = False
                csv_from_excel(to_Open)
                self.load_label['text'] = "Selected File: "+ file_name
                input_file = open("pretest.csv").readlines()
                load_everything_in()
                pick_12()
            else:
                self.incorrect_file = True
                self.load_label['text'] = 'Current file: ' + file_name + '\nPlease select an Excel file (.xlsx)'

class TrainingInstructionsWindow(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent, self.controller = parent, controller
        with open('instructions/training_instructions.txt', 'r') as f:
            data = f.read()
        self.controller.bind('<Return>',self.proceed_to_training)
        ttk.Label(self, text = "Training instructions").grid()
        training_instructions = ScrolledText(self, borderwidth=10, 
                font = "Helvetica", width=40, wrap = tk.WORD)
        training_instructions.insert(tk.END, data)
        training_instructions.grid()
        replay_button = ttk.Button(self, text = "Replay instructions",
            command = lambda: play_audio("instructions_audio_files/",
                                         "directions_training.wav"))
        self.ready_button = ttk.Button(self, text = 'Ready', 
                command = self.controller.start_training, state='disabled')
        self.ready_button.grid()
        self.controller.after(500, self.play_training_instructions)

    def play_training_instructions(self, *args):
        play_audio("instructions_audio_files/directions_training.wav", wait = True)
        self.controller.after(3000, self.enable_ready_button)

    def enable_ready_button(self, *args):
        self.ready_button['state'] = 'normal'
        
    def proceed_to_training(self, *args): 
        self.controller.start_training()

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


class TrainingModel:
    def __init__(self, controller):
        self.controller = controller
        self.controller.root.assigned_nouns = use_pretest_nouns(self.controller.root.assigned_nouns)
        self.nouns = self.controller.root.assigned_nouns
        
        self.results = []

    def myGenerator(self):
        for noun in self.nouns:
           if noun.pretest_correct == False:
              photo = PIL.ImageTk.PhotoImage(PIL.Image.open(noun.img))
              if noun.variability == "high":
                 for audio in noun.audios:
                    yield noun, photo, audio 
              elif noun.variability == "low":
                 audio = random.choice(noun.audios)
                 for i in range(10):
                    yield noun, photo, audio 

class TrainingView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent, self.controller = parent, controller
        self.controller.root.title('Training')
        self.ImageBox = ttk.Label(self)
        self.ImageBox.grid()
    
class TrainingController:
    def __init__(self, root):
        self.root = root
        self.model = TrainingModel(self)
        self.view = TrainingView(root.container, self)
        self.mylist = list(self.model.myGenerator())
        print()
        print()
        print()
        for word in self.mylist:
            print(word[0].name)
        
        random.shuffle(self.mylist)
        self.no_reps(self.mylist)
        i = 0
        for word in self.mylist:
            #print(word[0].name)
            i += 1
        
            #print("here",i)
            #print()

        self.iterator = iter(self.mylist)
        self.set_image()
    
    def no_reps(self, in_list):
        i = 0
        while i < len(in_list)-1:
           if i != len(in_list):
              if(in_list[i][0].name == in_list[i+1][0].name):
                 temp = in_list.pop(i+1)
                 in_list.append(temp)
           i += 1

 
    
    def set_image(self):
        try:
            noun, photo, audio = next(self.iterator) 
            mydict = {
                    'Word' : noun.name,
                    'Talker' : (audio.split('.')[0]).split('_')[1],
                    'Variability' : noun.variability,
                    }
            self.model.results.append(mydict)
            self.view.ImageBox.configure(image = photo)
            self.view.ImageBox.image=photo
            self.root.after(1000, self.play_image_audio, audio)
        except StopIteration:
            #df = pd.DataFrame(self.model.results, 
            #        columns = ['Word', 'Talker', 'Variability'])
            #df.to_excel(self.root.writer, 'Training')
            self.root.show_post_test_production_instructions()
            pass

    def play_image_audio(self, filepath):
        wave_obj = sa.WaveObject.from_wave_file(filepath)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        self.set_image()

    def ready(self, *args):
        self.view.ready_button.destroy()

class PostTestProductionInstructions(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid(column = 0, row = 0)
        # Define the elements
        self.ImageBox = ttk.Label(self)
        self.ImageBox.grid()
        photo = PIL.ImageTk.PhotoImage(
                PIL.Image.open('fixation_images/fixationpic_pencil1.jpg'))
        self.ImageBox.configure(image = photo)
        self.ImageBox.image=photo
        
        wave_obj = sa.WaveObject.from_wave_file(
                'instructions_audio_files/directions_posttestproduction.wav')
        play_obj = wave_obj.play()

        ttk.Button(self, text = 'Ready', 
                command = self.controller.start_post_test_production).grid()
        self.controller.bind('<Return>', self.continue_command)

    def continue_command(self, *args):
        self.controller.start_post_test_production()

class PostTestProductionModel:
    def __init__(self, assigned_nouns):
        self.nouns = iter(assigned_nouns)
        self.result_dicts = []

class PostTestProductionView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent, self.controller = parent, controller

        self.SpellingEntry = ttk.Entry(self, width=15, font = "Helvetica 25")
        self.SpellingEntry.grid(row=1, column=0)
        self.SpellingEntry.focus()
        self.EnterButton = ttk.Button(self, text = 'Enter')
        self.EnterButton.grid(row=1, column=1)


        


    def set_image(self,noun):
        self.noun = noun
        photo = PIL.ImageTk.PhotoImage(PIL.Image.open(self.noun.img))
        self.ImageBox = ttk.Label(self, image = photo)
        self.ImageBox.image=photo
        self.ImageBox.grid(row=0,columnspan=2,
                           padx=10,pady=10,sticky="nsew")

class PostTestProductionController:
    def __init__(self, root):
        self.root = root
        self.model = PostTestProductionModel(self.root.assigned_nouns)
        self.view = PostTestProductionView(root.container, self)
        self.NextWord()
        self.view.EnterButton.config(command=self.test_spelling)
        root.bind('<Return>', self.test_spelling)
        self.view.set_image(self.noun)

    def start_post_test_production(self):
        random.shuffle(self.root.assigned_nouns)
        for noun in assigned_nouns:
            wave_obj = sa.WaveObject.from_wave_file(noun.novel_talker)
            play_obj = wave_obj.play()
            play_obj.wait_done()

    def test_spelling(self, *args):
        spelling = self.view.SpellingEntry.get()
        self.view.SpellingEntry.delete(0, 'end')
        if len(spelling) > 0 and (spelling.isalpha() or " " in spelling):
            mydict = {
                        'Word' : self.noun.name,
                        'Length' : self.noun.length,
                        'Participant Answer' : spelling,
                        'Condition' : self.noun.variability,
                        }
            if spelling.lower() == self.noun.name.lower():
                mydict['T/F'] = 1
                self.model.result_dicts.append(mydict)
                self.production_spelling_is_correct = True
            else:
                mydict['T/F'] = 0
                self.model.result_dicts.append(mydict)
                self.production_spelling_is_correct = False
            self.noun.production_spelling = spelling
            self.NextWord()

    def NextWord(self, *args):
        try:
            self.noun = next(self.model.nouns)
            self.view.set_image(self.noun)
            play_audio(self.noun.novel_talker)
            print(self.noun.name)
        except StopIteration:
            print('Post-test production module finished')
            #self.model.results = pd.DataFrame(self.model.result_dicts,
            #        columns = ['Word', 'T/F', 'Participant Answer', 'Condition'])
            #self.model.results.to_excel(self.root.writer, 'Post-Test Production')

            #with open(str(self.root.LoginWindow.participant_code)\
            #        +'_production_results.txt','w') as f:
            #    for word in self.model.results:
            #        f.write(str(word)+'\n')
            #self.root.show_post_test_perception_instructions()
            #pass
            for word in self.model.result_dicts:
                to_output.append(word)

            #with open(self.root.LoginWindow.participant_code.get()\
            #        +'_production_results.txt','w') as f:
            #        for word in self.model.result_dicts:
            #            f.write(str(word)+'\n')
            self.root.show_post_test_perception_instructions()
            pass
            print("finished with it")
    
    def disable_stuff(self):
        self.view.EnterButton.state(["disabled"]) 
        self.view.SpellingEntry.state(["disabled"]) 
        

    def enable_stuff(self):
        self.view.EnterButton.state(["!disabled"]) 
        self.view.SpellingEntry.state(["!disabled"]) 
     

class PostTestPerceptionInstructions(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid(column = 0, row = 0)
        # Define the elements
        self.ImageBox = ttk.Label(self)
        self.ImageBox.grid()
        photo = PIL.ImageTk.PhotoImage(PIL.Image.open('fixation_images'
                                        '/fixationpic_pencil2.jpg'))
        self.ImageBox.configure(image = photo)
        self.ImageBox.image=photo
        
        wave_obj = sa.WaveObject.from_wave_file('instructions_audio_files/'
                                        'directions_posttestrecognition.wav')
        play_obj = wave_obj.play()
        # play_obj.wait_done()

        ttk.Button(self, text = 'Ready', 
                command = self.controller.start_post_test_perception).grid()
        self.controller.bind('<Return>', self.proceed_to_post_test_perception)

    def proceed_to_post_test_perception(self, *args): 
        self.controller.start_post_test_perception()

class PostTestPerceptionModel:
    def __init__(self, assigned_nouns):
        random.shuffle(assigned_nouns)
        self.nouns = iter(assigned_nouns)
        self.list_of_words = []
        self.plausible_spellings_table = pd.read_csv('Stimuli/'
            'plausible_spellings.csv', index_col=0, header = None).T
        self.results = []

class PostTestPerceptionView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent, self.controller = parent, controller
        self.training = True
        self.controller.root.title('Post-Test Perception')
        self.ImageBox = ttk.Label(self)
        self.ImageBox.grid(row = 0, columnspan = 2)
        self.nextButton = tk.Button(self, text ="Select Word", command = self.sel)

        self.spellings = [tk.Radiobutton(self, text = "spelling_"+str(i), variable=self.controller.var,
            value = i, command=self.controller.sel, height = 1,
            width = 20, borderwidth=1, relief="solid", font = ('Helvetica', '20'))
            for i in range(0,6)]
        
       
        # Place the spellings in a grid
        self.spellings[0].grid(row = 2, column = 0)
        self.spellings[1].grid(row = 2, column = 1)
        self.spellings[2].grid(row = 3, column = 0)
        self.spellings[3].grid(row = 3, column = 1)
        self.spellings[4].grid(row = 4, column = 0)
        self.spellings[5].grid(row = 4, column = 1)
       
        self.ready_button = ttk.Button(self, text="Ready",
                command=self.controller.set_first_image)

    def sel(self):
        self.controller.check_spelling(self.controller.var.get())
    


class PostTestPerceptionController:
    def __init__(self, root):
        self.root = root
        self.var = StringVar()
        self.model = PostTestPerceptionModel(self.root.assigned_nouns)
        self.view = PostTestPerceptionView(root.container, self)
        self.set_training_image()

    def set_training_image(self):
        self.noun = 'earth'
        photo = PIL.ImageTk.PhotoImage(PIL.Image.open('fixation_images/'
            'earthpic1.jpg')) 
        audio = 'instructions_audio_files/directions_Earth.wav'
        self.view.ImageBox.configure(image = photo)
        self.view.ImageBox.image=photo
        play_audio(audio)
        self.model.plausible_spellings = ['earth','erth','ert','urth','urt','earthe']
        random.shuffle(self.model.plausible_spellings)
        for i in range(0,6):
            word = self.model.plausible_spellings[i],
            self.view.spellings[i].config(text = word, value = word )

    def set_first_image(self, *args):
        """ Set the first image and remove the 'Ready' button """
        self.set_image()
        self.view.ready_button.destroy()
        self.view.nextButton.grid(row = 5, columnspan = 2)

    def sel(self):
        selection = "You have selected "+ str(self.var.get())
        self.check_spelling(self.var.get())
        print(selection)
    
    def set_image(self, *args):
        self.noun = next(self.model.nouns)
        photo = PIL.ImageTk.PhotoImage(PIL.Image.open(self.noun.img)) 
        audio = self.noun.novel_talker
        self.view.ImageBox.configure(image = photo)
        self.view.ImageBox.image=photo
        wrong_spellings = self.model.plausible_spellings_table[
                self.noun.name.lower()].tolist()
        self.model.plausible_spellings = [self.noun.name]
        if not self.noun.production_spelling_is_correct:
            self.model.plausible_spellings.append(self.noun.production_spelling)
            self.model.plausible_spellings+= random.sample(wrong_spellings, 4)
        else:
            self.model.plausible_spellings.append(wrong_spellings)
        random.shuffle(self.model.plausible_spellings)
        for i in range(0,6):
            to_put = self.model.plausible_spellings[i].lower()
            self.view.spellings[i].config(
                    text = to_put, value = to_put)
        self.root.after(500, self.play_image_audio, audio)

    def Nothing(self):
        return

    def check_spelling(self, word):
        mydict = {}
        selected_spelling = word
        mydict['Participant Answer'] = selected_spelling
        print(selected_spelling)
        mydict['Choices'] = ', '.join(self.model.plausible_spellings)

        if self.noun == 'earth':
            mydict['Word'] = 'Earth'
            mydict['Condition'] = 'short'
            if selected_spelling == 'earth':
                mydict['T/F'] = 1
                play_audio('instructions_audio_files/directions_goodnowlets.wav')
                #self.view.nextButton.destroy()
                self.view.ready_button.grid(row = 5, columnspan = 2)
                for i in range(0,6):
                   self.view.spellings[i].config(command = self.Nothing ) 
            else:
                mydict['T/F'] = 0
                play_audio('instructions_audio_files/directions_oops.wav')
                #self.view.nextButton.destroy()
            self.model.results.append(mydict)
        else:
            for dic in to_output:
                if self.noun.name == dic['Word']:
                   dic['Forced'] = selected_spelling
            mydict['Word'] = self.noun.name
            mydict['Condition'] = self.noun.variability
            if self.noun.name == selected_spelling:
                mydict['T/F'] = 1
            else:
                mydict['T/F'] = 0
            self.model.results.append(mydict)

            try:
                self.set_image()
            except StopIteration:
                print('post test perception finished')
                #self.model.results_dataframe = pd.DataFrame(self.model.results,
                #        columns = ['Word', 'T/F', 'Participant Answer', 
                #                   'Choices', 'Condition'])
                #self.model.results_dataframe.to_excel(self.root.writer,
                #        'Post-Test Perception')
                print("figure out how to write the output")
                self.root.show_final_screen()

    def play_image_audio(self, filepath):
        wave_obj = sa.WaveObject.from_wave_file(filepath)
        play_obj = wave_obj.play()
                
class FinalScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid(column = 0, row = 0)
        # Define the elements
        tk.Label(self, text = "Thank you for your time", height = 10, width = 20, 
                font = ("Helvetica", "20")).grid()

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.container = ttk.Frame(self, height = 300, width = 400)
        self.container.grid()
        self.show_login_window()
        self.examiner = 'default_examiner'
        self.participant_code = 'default_participant_code'
        self.assigned_nouns = assign_nouns(short_nouns, long_nouns)
        #for noun in self.assigned_nouns:
        #   print(noun)
        self.writer = None

    def show_login_window(self):
        self.LoginWindow = LoginWindow(self.container, self)
        self.title('Login')
        self.LoginWindow.grid(row = 0, column = 0, sticky = "nsew")
    
    def show_training_instructions(self):
        self.TrainingInstructionsWindow = TrainingInstructionsWindow(
                self.container, self)
        self.title("Training instructions")
        self.TrainingInstructionsWindow.grid(row = 0, column = 0, sticky = "nsew")
        self.TrainingInstructionsWindow.tkraise()
    
    def start_training(self):
        self.TrainingController = TrainingController(self)
        self.title("Training")
        self.TrainingController.view.grid(row=0,column=0,sticky="nsew")
        self.TrainingController.view.tkraise()

    def show_post_test_production_instructions(self):
        self.PostTestProductionInstructions= PostTestProductionInstructions(
                self.container, self)
        self.title("Post Test Production Instructions")
        self.PostTestProductionInstructions.grid(row = 0, column = 0, sticky = "nsew")
        self.PostTestProductionInstructions.tkraise()

    def start_post_test_production(self):
        self.PostTestProductionController = PostTestProductionController(self)
        self.title("Post Test Production")
        self.PostTestProductionController.view.grid(row=0,column=0,sticky="nsew")
        self.PostTestProductionController.view.tkraise()

    def show_post_test_perception_instructions(self):
        self.PostTestPerceptionInstructions= PostTestPerceptionInstructions(
                self.container, self)
        self.title("Post Test Perception Instructions")
        self.PostTestPerceptionInstructions.grid(row = 0, column = 0, sticky = "nsew")
        self.PostTestPerceptionInstructions.tkraise()

    def start_post_test_perception(self):
        self.PostTestPerceptionController = PostTestPerceptionController(self)
        self.title("Post Test Perception")
        self.PostTestPerceptionController.view.grid(row=0,column=0,sticky="nsew")
        self.PostTestPerceptionController.view.tkraise()

    def final_output(self):
        output_file = open("output_test/" + self.LoginWindow.participant_code.get()\
            +"_test_results.csv",'w')
        output_file.write("Condition,Ortho Target,Ortho Production,Forced\n")
        for word in to_output:
            output_file.write(word['Condition']+ "," + word['Word']+ "," +\
                word['Participant Answer']+ "," + word['Forced']+"\n")
        output_file.close()

    def show_final_screen(self):
        self.FinalScreen = FinalScreen(self.container, self)
        self.title("Final Screen")
        self.FinalScreen.grid(row = 0, column = 0, sticky = "nsew")
        #self.writer.save()
        #time.sleep(5)
        self.final_output()
        #with open(self.LoginWindow.participant_code.get()\
        #    +'_production_results.txt','w') as f:
        #    for word in to_output:
        #        f.write(str(word)+'\n')
        #print(len(to_output))
        
        #for word in to_output:
        #    print(str(word)) 
        print("done")
        #exit()

if __name__=="__main__":
    app = MainApplication()
    app.mainloop()
