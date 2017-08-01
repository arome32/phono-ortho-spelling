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

# List of nouns, divided into short and long nouns

nouns = {}

df = pd.read_csv('word_list.csv', encoding = 'utf-8')

nouns['short'] = df[df['phonemes'] >= 9]['Word'].tolist()
nouns['long'] = df[df['phonemes'] <= 8]['Word'].tolist()

short_nouns = [Noun(name.capitalize(),'short') for name in nouns['short']]
long_nouns = [Noun(name.capitalize(),'long') for name in nouns['long']]

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
                text = "Participant Code:", padding = 10)
        self.participant_code_entry = ttk.Entry(self,
                width=20, textvariable = self.participant_code)

        # Create text field for entering the examiner name
        self.examiner = tk.StringVar()
        self.examiner_entry = ttk.Entry(self, width=20,
                textvariable = self.examiner)
        self.examiner_label = ttk.Label(self, text="Examiner:", padding = 10)
        self.login_button = ttk.Button(self, text="Login", command=self.login)

        # Arrange the elements
        title.grid(row = 0, columnspan = 3, pady = 5)
        self.participant_code_label.grid(row=1, column=1, sticky=tk.E, padx= 1)
        self.participant_code_entry.grid(row = 1, column = 2, padx = 1)
        self.examiner_label.grid(row = 2, column = 1,sticky = tk.E, padx = 1)
        self.examiner_entry.grid(row = 2, column = 2, padx = 1)
        self.login_button.grid(row = 3, column = 2, pady = 10)
        self.controller.bind('<Return>', self.login)
        self.participant_code_entry.focus()

    def login(self, *args):
        self.controller.show_pretest_instructions()
        self.controller.participant_code = self.participant_code_entry.get()
        self.controller.examiner = self.examiner_entry.get()

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
        play_audio("instructions_audio_files/directions_pretest.wav")

        self.continue_button = ttk.Button(self, text = "Continue",
                command = self.continue_command)
        replay_button = ttk.Button(self, text = "Replay test words",
            command = lambda: play_audio("instructions_audio_files/",
                                         "directions_pretest.wav"))
        self.controller.bind('<Return>',self.continue_command)
        self.continue_button.grid()

        # Arrange elements
        replay_button.grid()

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
        self.controller = controller
        self.nouns = self.controller.root.assigned_nouns
        random.shuffle(self.nouns)
        self.nouns = iter(self.nouns) ; self.noun = next(self.nouns)
        self.records, self.n_wrong = {}, 0
        self.dicts = []

    def NextNoun(self, spelling):
        mydict = {  
                    'Word' : self.noun.name,
                    'Length' : self.noun.length,
                    'Participant Answer' : spelling,
                    'Condition' : self.noun.variability,
                 }
        try:
            if spelling.lower() == self.noun.name.lower():
                mydict['T/F'] = 1
                self.dicts.append(mydict)
                self.noun = next(self.nouns)
            else:
                mydict['T/F'] = 0
                self.dicts.append(mydict)
                self.n_wrong += 1
                if self.n_wrong > 4:
                    print('condition met!')
                    self.controller.do_post_processing()
                    return
                try: 
                    self.noun = next(self.nouns)
                except StopIteration:
                    try: 
                        self.noun = next(self.nouns)
                    except StopIteration:
                        print('done with iteration!')
                        self.controller.do_post_processing()
                        return
        except StopIteration:
            print('done with iteration!')
            self.controller.do_post_processing()
            return

class PretestView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.EnterButton = ttk.Button(self, text = 'Enter')
        self.EnterButton.grid(row=2, column=1)
        self.SpellingEntry = ttk.Entry(self, width=8)
        self.SpellingEntry.grid(row=1, column=1)

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
        root.bind('<Return>', self.NextImage)
        self.view.SpellingEntry.focus()
        self.play_noun_audio()

    def NextImage(self, *args):
        spelling = self.view.SpellingEntry.get()
        self.view.SpellingEntry.delete(0, 'end')

        if len(spelling) > 0 and spelling.isalpha():
            self.view.SpellingEntry.delete(0, 'end')
            self.model.NextNoun(spelling)
            if self.model.n_wrong < 5:
                self.play_noun_audio()
            print(self.model.noun.name)
            self.view.set_image(self.model.noun)
            self.view.ImageBox.grid(row=0, columnspan=2, padx=10,
                                    pady=10, sticky="nsew")


    def do_post_processing(self):
        """ Do post-processing. Does the participant meet the criteria for 
            the study? """
        self.model.results = pd.DataFrame(self.model.dicts,
                columns = ['Word', 'T/F', 'Participant Answer', 'Condition'])
        self.root.filename = self.root.participant_code+'_'+self.root.examiner
        self.root.writer = pd.ExcelWriter(self.root.filename+'.xlsx')
        self.model.results.to_excel(self.root.writer, 'Pretest')

        if self.model.n_wrong < 4: 
            self.root.show_thankyou_screen(False)
            self.root.writer.save()
            os.rename(self.root.filename+'.xlsx',self.root.filename+'_CNM.xlsx')
        else:
            print('else')
            self.root.show_thankyou_screen(True)
            self.root.end_pretest()

    def play_noun_audio(self):
        try:
            audiofile = random.choice(self.model.noun.audios)
            play_audio(audiofile)
        except: 
            pass

class EndPretestWindow(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller

        self.label = ttk.Label(self, text = "Pretest done")
        self.label.grid()
        self.training_button = ttk.Button(self,
                text = 'Proceed to Training Instructions',
                command=self.proceed_to_training_instructions)
        self.training_button.grid()
        self.controller.bind('<Return>',self.proceed_to_training_instructions)

    def proceed_to_training_instructions(self, *args):
        self.controller.show_training_instructions()

class ThankYouScreen(ttk.Frame):
    def __init__(self, parent, controller, condition_met):
        super().__init__(parent)
        self.controller = controller
        self.grid(column = 0, row = 0)
        # Define the elements
        if condition_met:
            ttk.Label(self, 
                text = "Thank you. Please get ready for the training").grid()
            ttk.Button(self, text = "Proceed to Training").grid()
        else:
            ttk.Label(self, text = "Thank you for your help.").grid()
            ttk.Button(self, text = "Exit program", 
                    command = self.controller.quit).grid()

class TrainingInstructionsWindow(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent, self.controller = parent, controller
        with open('training_instructions.txt', 'r') as f:
            data = f.read()
        self.controller.bind('<Return>',self.proceed_to_training)
        ttk.Label(self, text = "Training instructions").grid()
        training_instructions = ScrolledText(self, borderwidth=10, 
                font = "Helvetica", width=40, wrap = tk.WORD)
        training_instructions.insert(tk.END, data)
        training_instructions.grid()
        ttk.Button(self, text = 'Ready', 
                command = self.controller.start_training).grid()
        play_audio(normpath("instructions_audio_files/directions_training.wav"))

    def proceed_to_training(self, *args): 
        self.controller.start_training()

def splitList(xs: List) -> Tuple[List,List]:
    """ Randomly shuffle elements of list into two sublists."""
    random.shuffle(xs)
    length = len(xs)//2
    return xs[:length], xs[length:2*length]

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
        self.nouns = self.controller.root.assigned_nouns
        self.results = []

    def myGenerator(self):
        for noun in self.nouns:
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
        random.shuffle(self.mylist)
        self.iterator = iter(self.mylist[0:2])
        self.set_image()

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
            df = pd.DataFrame(self.model.results, 
                    columns = ['Word', 'Talker', 'Variability'])
            df.to_excel(self.root.writer, 'Training')
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

        self.SpellingEntry = ttk.Entry(self, width=8)
        self.SpellingEntry.grid(row=1, column=1)
        self.SpellingEntry.focus()
        self.EnterButton = ttk.Button(self, text = 'Enter')
        self.EnterButton.grid(row=2, column=1)

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
        if len(spelling) > 0 and spelling.isalpha():
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
            self.model.results = pd.DataFrame(self.model.result_dicts,
                    columns = ['Word', 'T/F', 'Participant Answer', 'Condition'])
            self.model.results.to_excel(self.root.writer, 'Post-Test Production')

            with open(str(self.root.LoginWindow.participant_code)\
                    +'_production_results.txt','w') as f:
                for word in self.model.results:
                    f.write(str(word)+'\n')
            self.root.show_post_test_perception_instructions()
            pass

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
        self.controller.root.title('Post-Test Perception')
        self.ImageBox = ttk.Label(self)
        self.ImageBox.grid(row = 0, columnspan = 2)
        self.spellings = [tk.Label(self, text = "spelling_"+str(i), height = 1,
            width = 20, borderwidth=1, relief="solid", font = ('Helvetica', '20'))
            for i in range(0,6)]
        for label in self.spellings:
            label.bind("<Button-1>",self.controller.check_spelling, label)

        # Place the spellings in a grid
        self.spellings[0].grid(row = 2, column = 0)
        self.spellings[1].grid(row = 2, column = 1)
        self.spellings[2].grid(row = 3, column = 0)
        self.spellings[3].grid(row = 3, column = 1)
        self.spellings[4].grid(row = 4, column = 0)
        self.spellings[5].grid(row = 4, column = 1)

        self.ready_button = ttk.Button(self, text="Ready",
                command=self.controller.set_first_image)


class PostTestPerceptionController:
    def __init__(self, root):
        self.root = root
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
            self.view.spellings[i].config(text = self.model.plausible_spellings[i])

    def set_first_image(self, *args):
        """ Set the first image and remove the 'Ready' button """
        self.set_image()
        self.view.ready_button.destroy()

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
            self.view.spellings[i].config(
                    text = self.model.plausible_spellings[i].lower())
        self.root.after(500, self.play_image_audio, audio)

    def check_spelling(self, label):
        mydict = {}
        selected_spelling = label.widget.cget("text")
        mydict['Participant Answer'] = selected_spelling
        mydict['Choices'] = ', '.join(self.model.plausible_spellings)

        if self.noun == 'earth':
            mydict['Word'] = 'Earth'
            mydict['Condition'] = 'short'
            if selected_spelling == 'earth':
                mydict['T/F'] = 1
                play_audio('instructions_audio_files/directions_goodnowlets.wav')
            else:
                mydict['T/F'] = 0
                play_audio('instructions_audio_files/directions_oops.wav')
            self.model.results.append(mydict)
            self.view.ready_button.grid(row = 5, columnspan = 2)

        else:
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
                self.model.results_dataframe = pd.DataFrame(self.model.results,
                        columns = ['Word', 'T/F', 'Participant Answer', 
                                   'Choices', 'Condition'])
                self.model.results_dataframe.to_excel(self.root.writer,
                        'Post-Test Perception')
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
        tk.Label(self, text = "Thank you", height = 10, width = 20, 
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
        self.writer = None
    def show_login_window(self):
        self.LoginWindow = LoginWindow(self.container, self)
        self.LoginWindow.grid(row = 0, column = 0, sticky = "nsew")
    def show_thankyou_screen(self, condition_met):
        self.ThankYouScreen = ThankYouScreen(self.container, self, condition_met)
        self.ThankYouScreen.grid(row = 0, column = 0, sticky = "nsew")
    def show_pretest_instructions(self):
        self.PretestInstructionsWindow=PretestInstructionsWindow(self.container,self)
        self.PretestInstructionsWindow.grid(row = 0, column = 0, sticky = "nsew")
        self.PretestInstructionsWindow.tkraise()
    def show_any_questions_window(self):
        self.AnyQuestionsWindow = AnyQuestionsWindow(self.container, self)
        self.AnyQuestionsWindow.grid(row = 0, column = 0, sticky = "nsew")
        self.AnyQuestionsWindow.tkraise()
    def start_pretest(self):
        self.PretestController = PretestController(self)
        self.PretestController.view.grid(row = 0, column = 0, sticky = "nsew")
        self.PretestController.view.tkraise()
    def end_pretest(self):
        self.EndPretestWindow = EndPretestWindow(self.container, self)
        self.EndPretestWindow.grid(row=0,column=0,sticky="nsew")
    def show_training_instructions(self):
        self.TrainingInstructionsWindow = TrainingInstructionsWindow(
                self.container, self)
        self.TrainingInstructionsWindow.grid(row = 0, column = 0, sticky = "nsew")
        self.TrainingInstructionsWindow.tkraise()
    def start_training(self):
        self.TrainingController = TrainingController(self)
        self.TrainingController.view.grid(row=0,column=0,sticky="nsew")
        self.TrainingController.view.tkraise()
    def show_post_test_production_instructions(self):
        self.PostTestProductionInstructions= PostTestProductionInstructions(
                self.container, self)
        self.PostTestProductionInstructions.grid(row = 0, column = 0, sticky = "nsew")
        self.PostTestProductionInstructions.tkraise()
    def start_post_test_production(self):
        self.PostTestProductionController = PostTestProductionController(self)
        self.PostTestProductionController.view.grid(row=0,column=0,sticky="nsew")
        self.PostTestProductionController.view.tkraise()
    def show_post_test_perception_instructions(self):
        self.PostTestPerceptionInstructions= PostTestPerceptionInstructions(
                self.container, self)
        self.PostTestPerceptionInstructions.grid(row = 0, column = 0, sticky = "nsew")
        self.PostTestPerceptionInstructions.tkraise()
    def start_post_test_perception(self):
        self.PostTestPerceptionController = PostTestPerceptionController(self)
        self.PostTestPerceptionController.view.grid(row=0,column=0,sticky="nsew")
        self.PostTestPerceptionController.view.tkraise()
    def show_final_screen(self):
        self.FinalScreen = FinalScreen(self.container, self)
        self.FinalScreen.grid(row = 0, column = 0, sticky = "nsew")
        self.writer.save()

if __name__=="__main__":
    app = MainApplication()
    app.mainloop()
