""" This is the main program for the phono-ortho-spelling project """

import os, PIL, random
from os.path import normpath
import pandas as pd
import simpleaudio as sa
from glob import glob
from PIL import Image, ImageTk
import itertools
import typing
from typing import List
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import pandas as pd

#==============================================================================
# Some helper functions
#==============================================================================

def play_audio(filepath):
    wave_obj = sa.WaveObject.from_wave_file(filepath)
    play_obj = wave_obj.play()

def splitlist(xs: List) -> List:
    """ Randomly shuffle elements of list into two sublists."""
    random.shuffle(xs)
    length = len(xs)//2
    return xs[:length], xs[length:2*length]

#==============================================================================
# Noun helper class and noun lists
#==============================================================================

class Noun(object):
    def __init__(self, name: str, length: int):
        self.name = name
        self.length = length
        self.img = "Stimuli/Active/{}/image + sound/pic_{}.jpg".format(
            self.name.capitalize(), self.name)
        self.audios = glob("Stimuli/Active/{}/image + sound/*.wav".format(
            self.name.capitalize()))
        random.shuffle(self.audios)
        # Randomly pick one talker as talker 11
        self.talker_11, *rest_of_talkers = self.audios
        self.audios = rest_of_talkers 

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
        photo = PIL.ImageTk.PhotoImage(PIL.Image.open(self.noun.img))
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
        self.controller.bind('<Return>',self.proceed_to_training)
        ttk.Label(self, text = "Training instructions").grid()
        ttk.Button(self, text = 'Ready', 
                command = self.controller.start_training).grid()
        play_audio(normpath("instructions_audio_files/training_instructions.wav"))

    def proceed_to_training(self, *args): 
        self.controller.start_training()

def assign_nouns(short_nouns, long_nouns):
    random.shuffle(short_nouns)
    random.shuffle(long_nouns)

    # split the lists into high and low variability sublists
    hi_variability_short, lo_variability_short = splitlist(short_nouns)
    hi_variability_long, lo_variability_long = splitlist(long_nouns)

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
        self.list_of_words = []

    def myGenerator(self, variability):
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
        self.mylist = list(self.model.myGenerator(random.choice(['HI','LO'])))
        random.shuffle(self.mylist)
        self.iterator = iter(self.mylist[0:2])
        self.set_image()

    def set_image(self):
        try:
            noun, photo, audio = next(self.iterator) 
            self.model.list_of_words.append((noun.name, audio, noun.variability))
            self.view.ImageBox.configure(image = photo)
            self.view.ImageBox.image=photo
            self.root.after(500, self.play_image_audio, audio)
        except StopIteration:
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
        photo = PIL.ImageTk.PhotoImage(PIL.Image.open('fixation_mark.jpg'))
        self.ImageBox.configure(image = photo)
        self.ImageBox.image=photo
        
        wave_obj = sa.WaveObject.from_wave_file('instructions_audio_files/post_test_production_instructions.wav')
        play_obj = wave_obj.play()
        # play_obj.wait_done()

        ttk.Button(self, text = 'Ready', 
                command = self.controller.start_post_test_production).grid()

class PostTestProductionModel:
    def __init__(self, assigned_nouns):
        self.nouns = iter(assigned_nouns)

class PostTestProductionView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent, self.controller = parent, controller

        self.SpellingEntry = ttk.Entry(self, width=8)
        self.SpellingEntry.grid(row=1, column=1)
        self.EnterButton = ttk.Button(self, text = 'Enter')
        self.EnterButton.grid(row=2, column=1)

class PostTestProductionController:
    def __init__(self, root):
        self.root = root
        self.model = PostTestProductionModel(self.root.assigned_nouns)
        self.view = PostTestProductionView(root.container, self)
        self.view.EnterButton.config(command=self.NextWord)
        # root.bind('<Return>', self.NextWord)

    def start_post_test_production(self):
        random.shuffle(self.root.assigned_nouns)
        for noun in assigned_nouns:
            wave_obj = sa.WaveObject.from_wave_file(noun.talker_11)
            play_obj = wave_obj.play()
            play_obj.wait_done()

    def NextWord(self, *args):
        spelling = self.view.SpellingEntry.get()
        self.view.SpellingEntry.delete(0, 'end')
        try:
            noun = next(self.model.nouns)
            print(noun.name)
            if spelling.lower() == noun.name.lower():
                print('Correct spelling!')
            else:
                print('Incorrect spelling!')
        except StopIteration:
            print('Post-test production module finished')
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
        photo = PIL.ImageTk.PhotoImage(PIL.Image.open('transition_image.jpg'))
        self.ImageBox.configure(image = photo)
        self.ImageBox.image=photo
        
        wave_obj = sa.WaveObject.from_wave_file('instructions_audio_files/post_test_perception_instructions.wav')
        play_obj = wave_obj.play()
        # play_obj.wait_done()

        ttk.Button(self, text = 'Ready', 
                command = self.controller.start_post_test_perception).grid()

class PostTestPerceptionModel:
    def __init__(self, assigned_nouns):
        random.shuffle(assigned_nouns)
        self.nouns = iter(assigned_nouns)
        self.list_of_words = []
        self.all_plausible_spellings = pd.read_csv('Stimuli/plausible_spellings.csv',
                index_col=0, header = None).T

class PostTestPerceptionView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent, self.controller = parent, controller
        self.controller.root.title('Post-Test Perception')
        self.ImageBox = ttk.Label(self)
        self.ImageBox.grid(row = 0, columnspan = 2)
        # self.EnterButton = ttk.Button(self, text = 'Next Word')
        # self.EnterButton.grid(row=8, columnspan=2)
        self.spellings = [tk.Label(self, text = "spelling_"+str(i), height = 10,
            width = 30, borderwidth=1, relief="solid") for i in range(0,6)]
        for label in self.spellings:
            label.bind("<Button-1>",self.controller.check_spelling, label)

        # Place the spellings in a grid
        self.spellings[0].grid(row = 2, column = 0)
        self.spellings[1].grid(row = 2, column = 1)
        self.spellings[2].grid(row = 3, column = 0)
        self.spellings[3].grid(row = 3, column = 1)
        self.spellings[4].grid(row = 4, column = 0)
        self.spellings[5].grid(row = 4, column = 1)


class PostTestPerceptionController:
    def __init__(self, root):
        self.root = root
        self.model = PostTestPerceptionModel(self.root.assigned_nouns)
        self.view = PostTestPerceptionView(root.container, self)
        self.noun = next(self.model.nouns)
        self.set_image()

    def set_image(self, *args):
        photo = PIL.ImageTk.PhotoImage(PIL.Image.open(self.noun.img)) 
        audio = self.noun.talker_11
        self.model.list_of_words.append((self.noun.name, audio, self.noun.variability))
        self.view.ImageBox.configure(image = photo)
        self.view.ImageBox.image=photo
        plausible_spellings = self.model.all_plausible_spellings[self.noun.name].tolist()+[self.noun.name]
        random.shuffle(plausible_spellings)
        for i in range(0,6):
            self.view.spellings[i].config(text = plausible_spellings[i])
        self.root.after(500, self.play_image_audio, audio)

    def check_spelling(self, label):
        if self.noun.name == label.widget.cget("text"):
            print('correct spelling')
        else:
            print('wrong spelling')

        try:
            self.noun = next(self.model.nouns)
            self.set_image()
        except StopIteration:
            print('post test perception finished')
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
        tk.Label(self, text = "Thank you", height = 50, width = 100).grid()

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.container = ttk.Frame(self)
        self.container.grid()
        self.show_login_window()
        self.assigned_nouns = assign_nouns(short_nouns, long_nouns)
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

if __name__=="__main__":
    app = MainApplication()
    app.mainloop()
