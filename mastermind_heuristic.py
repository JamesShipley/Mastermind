from timer_py import timer
from tree_drawer import tree_drawer
import time,math, random

def rand_pick(li):
    return li[random.randint(0,len(li)-1)]
def first(x):
    return x[0]

def flatten(t):
    return [i for sublist in t for i in sublist]

def unique(t):
    return [x for (i,x) in enumerate(t) if x not in t[:i]]

def map_(f,li):
    return [f(x) for x in li]

def average(t):
    return sum(t)/len(t)

def make_of_length(length,colours):
    if not length:
        return [""]
    return [str(i)+val for val in make_of_length(length-1,colours) for i in range(colours)]

    return [[i]+val for val in make_of_length(length-1,colours) for i in range(colours)]

def m_all(letters="abcd",to_go=4,so_far=""):
    if not to_go:
        return [so_far]
    a = m_all(letters,to_go-1,so_far+letters[0])
    b = m_all(letters[1:],to_go-1,so_far+letters[0]) if len(letters)>1 and to_go!=1 else []
    return  a+b

class mm_solver:
    def __init__(self):
        self.resp_grid = {}
        self.length = 4
        self.colours = 6
        self.max_candidates = 4
        self.size = self.colours**self.length
        self.populated = False
        self.guess_map = {}
        self.visited = 0
        self.branch_factor = {i:0 for i in range(20)}
        self.time_ded = 0

    def enc_state(self,s):
         return "".join(sorted(s))
    def uenc_state(self,s):
        return [s[i:i+self.length] for i in range(0,len(s),self.length)]
    
    def populate_resps(self):
        guesses = make_of_length(self.length,self.colours)
        
        for i in range(self.size):
            for j in range(i,self.size):
                g1,g2 = guesses[i],guesses[j]
                self.resp_grid[g1+g2 if g1<g2 else g2+g1] = self.get_base_resp(g1,g2)
        self.populated = True
   #base response
    def get_base_resp(self,g1,g2):
        g1,g2 = list(g1),list(g2)
        bw = 0
        for i in range(self.length):
            if g1[i]==g2[i]:
                g1[i] =-1
                g2[i] =-2
                bw+=10

        for x in g1:
            if x in g2:
                g2[g2.index(x)] = -2
                bw+=1
        return bw
    
    #lookup response
    def get_resp(self,g1,g2):
        return self.resp_grid[g1+g2 if g1<g2 else g2+g1] if self.populated else self.get_base_resp(g1,g2)
    

    #reduce
    def reduce(self,s,guess,resp):
        return [g for g in s if self.get_resp(g,guess)==resp]

    #grab responses from each code in s
    def resp_dist(self,s,guess):
        resp_g = {}
        for code in s:
            resp = self.get_resp(guess,code)
            resp_g[resp] = resp_g[resp]+1 if resp in resp_g else 1
        return resp_g
    
    #how much does a guess reduce the state space by on average
    def evaluate(self,s,guess):
        return len(s) - max([x for (resp,x) in self.resp_dist(s,guess).items()])

    def eval_state_inner(self,s,depth=0):
        if len(s)==1:
            return 1,s[0]
        if depth>6:
            return 10,""
        guess = max(big_s,key=lambda x:self.evaluate(s,x))
        #print(guess)
        return 1+ min([self.eval_state(self.reduce(s,guess,resp))[0] if resp!=40 else 0 for resp in self.resp_dist(s,guess).keys()]),guess
        
        sym1 = self.symmetries(s).items()
        #sym2 = self.symmetries(s,True).items()
        candidates = min(sym1,key=first)[1][:1]#[gs[0] for v,gs in sorted(sym1,key=first)]#[:self.max_candidates]
        #print(candidates)
        values = [(self.eval_guess(s,g,depth+1),g) for g in candidates]
        res,guess = min(values,key=first)
##        if not depth:
##            for v,g in values:
##                print("guess:{},val:{}".format(g,v))
                
        return res+1,guess
    
    def eval_state(self,s,depth=0):
        self.visited+=1
##        if not self.visited%1000:
##            print("----------",self.visited)
####            for (v,n) in self.branch_factor.items():
####                print("f:{},n:{}".format(v,n))
##            print("branch: {}".format(sum([v*n for v,n in self.branch_factor.items()])/sum([n for v,n in self.branch_factor.items()])))
        res,g = self.eval_state_inner(s,depth)
        self.guess_map[self.enc_state(s)] = g
        return res,g

    def eval_guess(self,s,g,depth):
        r_d = self.resp_dist(s,g).items()
        self.branch_factor[len(r_d)]+=1
        return sum([self.eval_state(self.reduce(s,g,resp),depth)[0]*x if resp!=40 else 0 for resp,x in r_d])/len(s)
        
    
    def symmetries(self,s,bigS=False):
        syms = {}
        for g in (s if not bigS else big_s):
            val = self.evaluate(s,g)
            syms[val] = [g]+(syms[val] if val in syms else [])
        return syms

m = mm_solver()
t = timer().start()
m.populate_resps()
print("populated",t.reset())
s = make_of_length(m.length,m.colours)
big_s = list(s)
#///
for (a,b) in m.resp_dist(s,"1122").items():
    print("resp:{},num:{}".format(a,b))
input()
#///
evaly,first_guess = m.eval_state(s)
print(t.stop(),"seconds")
total_guesses = 0
guess_distribution = {i:0 for i in range(1,12)}
for (j,code) in enumerate(s,1):
    current_guess = first_guess
    current_state = list(s)
    for i in range(1,12):
        #guessing
        before = len(current_state)
        #print("cur:{},code:{}".format(current_guess,code))
        resp = m.get_resp(current_guess,code)
        if resp==40:
            break
        current_state = m.reduce(current_state,current_guess,resp)
        #print("current_state:{}, guessing:{}, resp:{},new_state:{}".format(before,current_guess,resp,len(current_state)))
        current_guess = m.guess_map[m.enc_state(current_state)]

    total_guesses +=i
    guess_distribution[i]+=1

    #print("n:{}, g:{},avg:{}".format(j,i,total_guesses/j))
for (n,i) in sorted(guess_distribution.items(),key=(lambda x:x[0])):
    print("guesses: {}, number:{}".format(n,i))
print("eval:{}, est:{}".format(sum([n*i for (n,i) in guess_distribution.items()])/m.size,evaly))
print("visited: {}, time :{} ".format(m.visited,m.time_ded))
##code = s[random.randint(0,m.size-1)]
##while True:
##    ev = input("eval?")=="y"
##    print("state space is ",len(s))
##    
##    _,g = m.make_guess(s)
##    if ev:
##        bg,v = m.best_guess(s)
##        print("best guesses:",bg)
##        print("your guess v:{} ,best guess v:{}".format(m.eval_a_guess(g,s),v))
##    resp = m.get_resp(g,code)
##    s = m.reduce(s,g,resp)
##    print("you guessed ",g)
##    print("resp was",resp)
##    print("reduced down to :",len(s))

