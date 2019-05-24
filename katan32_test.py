from pycryptosat import Solver
from dp_functions import *
import gc

WORDSIZE=32
KEYSIZE=80

def binary_show(input):
  output=[]
  dec = int( input, 16);
  str_bin=str(bin(dec))
  bin_rep=str_bin[2:]
  for i in range(WORDSIZE):
   if bin_rep[i]=='1':
    output.append(31-i)

  return output
  

if __name__ == "__main__":
 # input
 Maxterm="FFFFFEFA" 
 rounds=80
 C_out=11

 Active_bits=binary_show(Maxterm)
 Involved_keys=[]
 for keybit_index in range(0,80) :
        print("Checking keybit at "+str(keybit_index)+"...")
        gc.collect()
        key_bit = [keybit_index]     
        satsolver = Solver()
        for i in range(WORDSIZE):
         if (i in Active_bits) : 
          zerotype[i]=0
         else:
          zerotype[i]=1

        state_update(satsolver, rounds)

        zero_bits = [x for x in range(KEYSIZE+WORDSIZE) if (x not in Active_bits  and (x-32) not in key_bit)]
        for i in zero_bits:
            satsolver.add_clause([-round_states[0][i]])
        for i in key_bit:
            satsolver.add_clause([round_states[0][i+WORDSIZE]])
        for i in Active_bits:
            satsolver.add_clause([round_states[0][i]])            

        Target_vector = [round_states[rounds][j] if C_out == j else -round_states[rounds][j] for j in range(WORDSIZE)]
        Target_vector += [-round_states[rounds][j+WORDSIZE] for j in range(KEYSIZE)]

        satisfiable, solution = satsolver.solve(Target_vector)
        if  satisfiable:
           Involved_keys.append(keybit_index)

        del satsolver

 print Involved_keys



