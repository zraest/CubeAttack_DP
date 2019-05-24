from pycryptosat import Solver


###  Katan32 specification
WORDSIZE=32
KEYSIZE=80
x1=31; x2=26; x3=27; x4=24; x5=22;
y1=18; y2=7; y3=12; y4=10; y5=8; y6=3;

IR = (
    1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1,
    0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0,
    1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0,
    0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1,
    0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1,
    1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1,
    0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0,
    1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1,
    0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1,
    1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1,
    1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1,
    0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1,
    1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0,
    0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1,
    0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1,
    1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0,
)



###define global variables
state_size=KEYSIZE+WORDSIZE
temporary_size=13
zerotype=[0 for _ in range(WORDSIZE)]
temporaries = ["t"+str(i+1) for i in range(temporary_size)]
state_variables=["s"+str(i) for i in range(state_size)]


round_states =[]
next_variable = 1
state_bit = [i + 1 for i in range(state_size)]
temporary = {i: None for i in temporaries}



def dpcopy(solver, source, target):
        """ When target != source, we have the following allowed trails
            on source, target:
              0 0 -> 0 0
              1 0 -> 0 1
              1 0 -> 1 0
            In particular, when the target is a state bit, it cannot be equal
            to 1.
        """
        if target == source:
            return
        old_source, new_source = get_variables(source)
        old_target, new_target = get_variables(target)
        #Ensure old target is 0
        if old_target != None:
            solver.add_clause([-old_target])
        solver.add_clause([-old_source, new_source, new_target])
        solver.add_clause([old_source, -new_source])
        solver.add_clause([old_source, -new_target])
        solver.add_clause([-new_source, -new_target])
        return
        
def dpxor(solver, source_1, source_2, target):
        """ First move source_2 to target, then apply the following
            rules on source_1, target:
              0 0 -> 0 0
              0 1 -> 0 1
              1 0 -> 1 0
              1 0 -> 0 1
              1 1 -> 1 1
        """
        if source_1 == source_2:
            old_target, new_target = get_variables(target)
            solver.add_clause([-new_target])
            return
        if source_1 != target:
            dpcopy(solver, source_2, target)
            source = source_1
        else:
            source = source_2
        old_source, new_source = get_variables(source)
        old_target, new_target = get_variables(target)
        solver.add_clause([-new_source, old_source])
        solver.add_clause([new_target, -old_target])
        solver.add_clause([-new_source, -new_target, old_target])
        solver.add_clause([new_source, new_target, -old_source])
        solver.add_clause([new_source, -new_target, old_source, old_target])
        solver.add_clause([new_source, -new_target, -old_source, -old_target])
        return
        
def dpand(solver, source_1, source_2, target):
        """ First move source_2 to target, then apply the following
            rules on source_1, target:
              0 0 -> 0 0
              0 1 -> 0 1
              1 0 -> 1 0
              1 0 -> 0 1
              1 1 -> 0 1
        """
        if source_1 == source_2:
            dpcopy(solver, source_1, target)
            return
        if source_1 != target:
            dpcopy(solver, source_2, target)
            source = source_1
        else:
            source = source_2
        old_source, new_source = get_variables(source)
        old_target, new_target = get_variables(target)
        solver.add_clause([-new_source, old_source])
        solver.add_clause([new_target, -old_target])
        solver.add_clause([-new_source, -new_target])
        solver.add_clause([new_source, new_target, -old_source])
        solver.add_clause([new_source, -new_target, old_source, old_target])
        return
    

    
def get_variables(bit):
        global  next_variable
        if bit[0] == 's':
            number = int(bit[1:])
            old_bit = state_bit[number] 
            new_bit = next_variable
            state_bit[number] = new_bit
            next_variable += 1
        elif bit[0] == 't':
            old_bit = temporary[bit] 
            new_bit = next_variable
            temporary[bit] = new_bit
            next_variable += 1
        return old_bit, new_bit




def state_update(solver, rounds):
    global  next_variable
    global state_bit
    global temporary

    next_variable = 1
    state_bit = [i + 1 for i in range(state_size)]
    temporary = {i: None for i in temporaries}
    state = [state_bit[i] for i in range(state_size)]
    round_states.append(state)
    next_variable += state_size

    for i in range(rounds):
      if i>39: # After 40 round, key bits are calculated based on key schedule
       for j in [0,1]: 
         dpxor(solver, state_variables[WORDSIZE+(2*(i%40)+j+19)%KEYSIZE],state_variables[WORDSIZE+(2*(i%40)+j+67)%KEYSIZE],"t"+str(2*j+1))
         dpxor(solver, state_variables[WORDSIZE+(2*(i%40)+j+30)%KEYSIZE],"t"+str(2*j+1),"t"+str(2*j+2))
         dpxor(solver, state_variables[WORDSIZE+(2*(i%40)+j)%KEYSIZE],"t"+str(2*j+2),state_variables[WORDSIZE+(2*(i%40)+j)%KEYSIZE])           

        
      if zerotype[x3]== 0 and zerotype[x4]==0:        
         dpand(solver, state_variables[x3],state_variables[x4],"t5")
         dpxor(solver, state_variables[x2],"t5","t6")
         if IR[i]==1:
          dpxor(solver, state_variables[x5],"t6","t7")
          dpxor(solver, state_variables[WORDSIZE+2*(i%40)],"t7","t8")
         else:
          dpxor(solver, state_variables[WORDSIZE+2*(i%40)],"t6","t8")
         dpxor(solver, state_variables[x1],"t8", state_variables[x1])
         zerotype0=0
      else:
         if IR[i]==1:
          dpxor(solver, state_variables[x5],state_variables[x2],"t7")
          dpxor(solver, state_variables[WORDSIZE+2*(i%40)],"t7","t8")
          if zerotype[x2]== 0 or zerotype[x5]==0 or zerotype[x1]==0: 
           zerotype0=0
          else:
           zerotype0=1
         else:
          dpxor(solver, state_variables[x2],state_variables[WORDSIZE+2*(i%40)],"t8")
          if zerotype[x2]== 0 or zerotype[x1]==0: 
           zerotype0=0
          else:
           zerotype0=1
         dpxor(solver, state_variables[x1],"t8",state_variables[x1])

      if zerotype[y3]== 0 and zerotype[y4]==0 and zerotype[y5]== 0 and zerotype[y6]== 0 :        
         dpand(solver, state_variables[y3],state_variables[y4],"t9")
         dpand(solver, state_variables[y5],state_variables[y6],"t10")
         dpxor(solver, state_variables[y2],"t9","t11")
         dpxor(solver, state_variables[WORDSIZE+2*(i%40)+1],"t10","t12")
         dpxor(solver, "t11","t12","t13")
         dpxor(solver, state_variables[y1],"t13",state_variables[y1])
         zerotype19=0
      elif zerotype[y3]== 0 and zerotype[y4]==0:
         dpand(solver, state_variables[y3],state_variables[y4],"t9")
         dpxor(solver, state_variables[y2],"t9","t11")
         dpxor(solver, state_variables[WORDSIZE+2*(i%40)+1],"t11","t13")
         dpxor(solver, state_variables[y1],"t13",state_variables[y1])
         zerotype19=0
      elif zerotype[y5]== 0 and zerotype[y6]==0:
         dpand(solver, state_variables[y5],state_variables[y6],"t10")
         dpxor(solver, state_variables[WORDSIZE+2*(i%40)+1],"t10","t12")
         dpxor(solver, state_variables[y2],"t12","t13")
         dpxor(solver, state_variables[y1],"t13",state_variables[y1])
         zerotype19=0
      else:
         dpxor(solver, state_variables[y2],state_variables[WORDSIZE+2*(i%40)+1],"t13")
         dpxor(solver, state_variables[y1],"t13",state_variables[y1])
         if zerotype[y2]== 0 or zerotype[y1]==0: 
           zerotype19=0
         else:
           zerotype19=1

        
      for j in range(0,WORDSIZE-1):
         if j <> 12:
          zerotype[WORDSIZE-1-j]=zerotype[WORDSIZE-j-2]
      zerotype[19]=zerotype19
      zerotype[0]=zerotype0

      tmp31=state_bit[WORDSIZE-1]
      for j in range(0,WORDSIZE-1):
           state_bit[WORDSIZE-1-j]=state_bit[WORDSIZE-j-2]
      state_bit[0]=tmp31

      for tmp in temporary.values():
          if tmp !=None:
             solver.add_clause([-tmp])

      state = [state_bit[i] for i in range(state_size)]
      round_states.append(state)





