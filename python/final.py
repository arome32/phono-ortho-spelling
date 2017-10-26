import sys

def get_phono(phono, word):
   for line in phono:
      line = line.strip().split(',')
      if line[0].lower() == word.lower():
         return line[1]

def main(one, two, three):
   pretest = open(one).readlines() #open(sys.argv[1]).readlines()
   test = open(two).readlines() #open(sys.argv[2]).readlines()
   name = three #sys.argv[3]
   phono = open("Stimuli/orthography_and_phonology.csv").readlines()
   print(name)
   final = open("output_final/"+name+"_final.csv","w")

   PRE = "Pre,"
   POST = "Post,"

   to_write = "Phase,Condition,Ortho Target,Ortho Production,Production Correct,Phono Target,"+\
           "Phono production,Forced Selection,Forced Correct\n"
   final.write(to_write)
   for post in test[1:]:
      post = post.strip().split(",")
      pTarget = get_phono(phono, post[1])
      for pre in pretest[1:]:
         pre = pre.strip().split(",")
         to_write = ""
         if post[1].lower() == pre[1].strip('"').lower():
            to_write += PRE + "N/A,"+ pre[1] +","+ pre[2] +","  
            num = (int(float(pre[3].strip('"'))))
            if num == 1:
               to_write += "True," 
            elif num == 0:
               to_write += "False," 
            else:
               to_write += "N/A," 
            to_write += pTarget +",,N/A,N/A\n"
            final.write(to_write)
      to_write = POST + post[0] + "," + post[1] +","+ post[2] +","+ post[3] +\
      ","+ pTarget +",,"+ post[4] + ","+post[5] + "\n"
      final.write(to_write)
