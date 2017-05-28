""" This is the main program for the phono-ortho-spelling project """

import os, PIL, random
from os.path import normpath
import pandas as pd
import simpleaudio as sa
from glob import glob
from time import sleep
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

#==============================================================================
# Some helper functions
#==============================================================================

def play_audio(filepath):
    wave_obj = sa.WaveObject.from_wave_file(filepath)
    wave_obj.play()

def splitlist(li):
    """ Randomly shuffle elements of list into two sublists."""
    random.shuffle(li)
    length = len(li)//2
    return li[:length], li[length:2*length]

#==============================================================================
# Noun helper class and noun lists
#==============================================================================

class Noun(object):
    def __init__(self, name, length):
        self.name = name
        self.length = length
        self.img = "Stimuli/Active/{}/image + sound/pic_{}.jpg".format(self.name.capitalize(), self.name)
        self.audios = glob("Stimuli/Active/{}/image + sound/*.wav".format(self.name.capitalize()))

nouns = {}

nouns['short'] = [
        'dynein',
        'purine',
        'isotope',
        'reducer',
        'kinesin',
        'tertiary',
        'eukaryote',
        'oxidizer',
        ]

nouns['long'] = [
    'amphipathic',
    'cytoplasm',
    'hypertonic',
    'peroxisome',
    'chemiosmotic',
    ]

short_nouns = [Noun(name,'short') for name in nouns['short']]
long_nouns = [Noun(name,'long') for name in nouns['long']]

class LoginWindow(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid(column = 0, row = 0)

        # Define the elements
        title = ttk.Label(self,
                text = "Welcome to the Science Spelling Training")

        # Create text field for entering the participant code
        self.participant_code = tk.StringVar()
        self.participant_code_label = ttk.Label(self,
                text = "Participant Code:", style = "Label")
        self.participant_code_entry = ttk.Entry(self,
                width=20, textvariable = self.participant_code)

        # Create text field for entering the examiner name
        self.examiner = tk.StringVar()
        self.examiner_entry = ttk.Entry(self, width=20,
                textvariable = self.examiner)
        self.examiner_label = ttk.Label(self, text="Examiner:", style="Label")
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

        play_audio("instructions_audio_files/pretest_instructions.wav")
        play_audio("instructions_audio_files/test_words.wav")

        # Define elements
        with open('pretest_instructions.txt', 'r') as f: data = f.read()

        pretest_instructions = ScrolledText(self, borderwidth=10, 
                font = "Helvetica", width=40, wrap = tk.WORD)
            
        pretest_instructions.insert(tk.END, data)
        pretest_instructions.grid()

        self.continue_button = ttk.Button(self, text = "Continue",
                command = self.continue_command)
        replay_button = ttk.Button(self, text = "Replay test words",
         command=lambda: play_audio("instructions_audio_files/test_words.wav"))
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
        play_audio("instructions_audio_files/any_questions.wav")
        title = ttk.Label(self, text = "Any questions?")
        title.grid(row = 0, columnspan = 3, pady = 5)
        self.continue_button = ttk.Button(self, text = "Continue",
                command = self.continue_command)
        self.continue_button.grid()

    def continue_command(self, *args):
        self.controller.start_pretest()
class PretestModel:
    def __init__(self, controller):
        self.controller, self.nouns = controller, short_nouns + long_nouns
        random.shuffle(self.nouns)
        self.nouns = iter(self.nouns) ; self.noun = next(self.nouns)
        self.records, self.n_wrong = {}, 0
    def NextNoun(self, spelling):
        try:
            if spelling.lower() == self.noun.name.lower():
                print('correct spelling!')
                self.records[self.noun.name] = (spelling, self.noun.length, 1)
                self.noun = next(self.nouns)
            else:
                print('incorrect spelling!')
                self.records[self.noun.name] = (spelling, self.noun.length, 0)
                self.n_wrong = self.n_wrong + 1
                if self.n_wrong > 4:
                    print('condition met!')
                    self.controller.do_post_processing()
                    return
                try: self.noun = next(self.nouns)
                except StopIteration:
                    try: self.noun = next(self.nouns)
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

    def set_image(self,noun):
        self.noun = noun
        image = PIL.Image.open(self.noun.img)
        photo = PIL.ImageTk.PhotoImage(image)
        self.ImageBox = ttk.Label(self, image = photo)
        self.ImageBox.image=photo
        self.ImageBox.grid(row=0,columnspan=2,
                           padx=10,pady=10,sticky="nsew")

class PretestController:
    def __init__(self, root):
        self.model, self.root = PretestModel(self), root
        self.view = PretestView(root.container, self)
        self.view.set_image(self.model.noun)
        self.view.EnterButton.config(command=self.NextImage)
        root.bind('<Return>', self.NextImage)
        self.view.SpellingEntry.focus()
        self.play_noun_audio()
        print(self.model.noun.name)

    def NextImage(self, *args):
        spelling = self.view.SpellingEntry.get()
        self.view.SpellingEntry.delete(0, 'end')
        self.model.NextNoun(spelling)
        if self.model.n_wrong < 5: self.play_noun_audio()
        print(self.model.noun.name)
        self.view.set_image(self.model.noun)
        self.view.ImageBox.grid(row=0,columnspan=2,padx=10,pady=10,sticky="nsew")

    def do_post_processing(self):
        """ Do post-processing. Does the participant meet the criteria for 
            the study? """
        # self.root.unbind('<Return>')
        filename = self.root.participant_code+'_'+self.root.examiner
        if self.model.n_wrong < 4: 
            filename = filename+'_CNM'
            self.root.show_thankyou_screen(False)
        else:
            print('else')
            self.root.show_thankyou_screen(True)
            self.root.end_pretest()
            # self.root.EndPretestWindow.grid()
            # self.root.EndPretestWindow.tkraise()
            # self.root.EndPretestWindow.training_button.grid()
        # Record the words and wher they got them wrong
        with open(filename+'.txt','w') as f:
            for key in self.model.records: 
                f.write(key+','+str(self.model.records[key][0])+','+
                        str(self.model.records[key][1])+'\n')
    def play_noun_audio(self):
        try:
            audiofile = random.choice(self.model.noun.audios)
            play_audio(audiofile)
        except: pass

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

class TrainingInstructionsWindow(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent, self.controller = parent, controller
        self.controller.bind('<Return>',self.proceed_to_training)
        ttk.Label(self, text = "Training instructions").grid()
        ttk.Button(self, text = 'Ready', 
                command = self.controller.start_training).grid()
        play_audio(normpath("instructions_audio_files/training_instructions.wav"))

    def proceed_to_training(self, *args): self.controller.start_training()


class TrainingModel:
    def __init__(self, controller):
        self.controller = controller
        self.short_nouns = short_nouns
        self.long_nouns = long_nouns
        random.shuffle(self.short_nouns)
        random.shuffle(self.long_nouns)

        # split the lists into high and low variability sublists
        hi_variability_short, lo_variability_short = splitlist(self.short_nouns)
        hi_variability_long, lo_variability_long = splitlist(self.long_nouns)

        self.hi_variability = hi_variability_short+hi_variability_long
        self.lo_variability = lo_variability_short+lo_variability_long

        # Create and set the 'variability' parameter for the noun
        for noun in self.hi_variability:
            noun.variability = "high"
        for noun in self.lo_variability:
            noun.variability = "low"

        # Creating an iterator for the combined list of nouns
        self.nouns = self.hi_variability + self.lo_variability
        random.shuffle(self.nouns)
        # self.noun = next(self.nouns)

class TrainingView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        label = ttk.Label(self, text = "Training Window")
        label.grid(row=0, column=0)
        # Play audio corresponding to words
        
    def set_image(self,noun):
        self.noun = noun
        image = PIL.Image.open(self.noun.img)
        photo = PIL.ImageTk.PhotoImage(image)
        self.ImageBox = ttk.Label(self, image = photo)
        self.ImageBox.image=photo
        self.ImageBox.grid(row=0,columnspan=2,
                           padx=10,pady=10,sticky="nsew")

class TrainingController:
    def __init__(self, root):
        self.model = TrainingModel(self)
        self.root = root
        self.view = TrainingView(root.container, self)
        self.view.grid()
        for noun in self.model.nouns:
            self.view.set_image(noun)
        self.view.set_image(self.view.noun)
        # self.view.ready_button.config(command=self.begin_training)
        
    def ready(self, *args):
        self.view.ready_button.destroy()

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
                
class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.container = ttk.Frame(self)
        self.container.grid()
        self.show_login_window()
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
    # def show_post_test_production_instructions(self):

if __name__=="__main__":
    app = MainApplication()
    app.mainloop()
