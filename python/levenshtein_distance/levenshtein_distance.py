import sys
import tkinter as tk
import xlrd
from tkinter import filedialog
import csv


def open_file():
    global input_file
    root = tk.Tk()
    root.withdraw()
 
    file_path = filedialog.askopenfilename()
    return file_path
 
def csv_from_excel(path):
    wb = xlrd.open_workbook(path)
    sh = wb.sheet_by_name('Sheet1')
    your_csv_file = open('ld.csv', 'w')
    wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

    for rownum in range(sh.nrows):
        wr.writerow(sh.row_values(rownum))
    your_csv_file.close()





input_file = open_file()

csv_from_excel(input_file)

csv_file = 'ld.csv'


cur_sub = 0 #subject number to make the new file
in_file = None #the to be input file
out_file = None #the to be output file

# minimumEditDistance function
#     takes in two strings and finds the minimum edit 
#     distance between them
#
# Parameters:
#     s1: the correct spelling string
#     s2: the string that is spelled incorrect
#
# Returns the edit distance from s2 -> s1
def minimumEditDistance(s1,s2):
    if len(s1) > len(s2):
        s1,s2 = s2,s1
    distances = range(len(s1) + 1)
    for index2,char2 in enumerate(s2):
        newDistances = [index2+1]
        for index1,char1 in enumerate(s1):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1],
                                             distances[index1+1],
                                             newDistances[-1])))
        distances = newDistances
    return distances[-1]


def main():
   global in_file

   in_file = open(csv_file).readlines() #thows every line from the file into a list
   for i in range(1,len(in_file)):
      to_write = ""
      line = in_file[i].strip().split(",") #gets the current line splits it by ','
      
      if line[0] == "": #for empty lines
          continue

      line_sub = int(line[0].strip('"')[0]) 
      #gets the first 'cell' which should be the subject identifier
      
      if line_sub is not cur_sub: #if there is a new subject idenifier 
         createOutputFile(line_sub) #create a new file for that subject
      
      score1 = minimumEditDistance(line[3],line[4]) #find the score for the current pair of words
      score2 = minimumEditDistance(line[5],line[6]) #find the score for the current pair of words
      
      
      #creates the basic line to write to output
      to_write += line[1]+','+line[2]+','+line[3]+','+line[4]+','+str(score1)+','
      to_write += line[5]+','+line[6]+','+str(score2)+"\n"
      #   ^ this is kinda ugly to look at so I'll explain how this line looks
      
      #TEST PHASE,Condition,ORTHO Target ,Production,LD,PHONO,Phono production,LD
      #   ^ that's the basic look for each line 


      out_file.write(to_write) #write out the line to the current output file


# createOutputFile function
#     (Currently) takes in an integer that representns the current
#     subject and creates an output file for that subject
#
# Parameters:
#     new_subject: the current subject's number (identifier)
#                  Will be used to create the output file
#
# Returns None
def createOutputFile(new_subject):
   global cur_sub
   global in_file
   global out_file 
   
   cur_sub = new_subject 
   out_file = open("levenshtein_distance_"+str(cur_sub)+".csv","w")
   first_line = in_file[0].strip().split(",")
   to_write = ""
   for i in range(1, len(first_line)):
      cur_col = first_line[i]
      to_write += cur_col.strip() + ","
      if("Production" in cur_col or "production" in cur_col):
         to_write += "LD,"
   out_file.write(to_write[:-1]+'\n')
   #print(to_write[:-1])


main()


