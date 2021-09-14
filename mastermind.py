from timer_py import timer
from tree_drawer import tree_drawer
import time,math

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
        self.size = self.colours**self.length
        self.populated = False
        self.guess_map = {}

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

    #evaluate a guess
    def evaluate(self,s,guess):
        resp_g = {}
        for code in s:
            resp = self.get_resp(guess,code)
            resp_g[resp] = resp_g[resp]+1 if resp in resp_g else 1
        return sum([x**2 for (v,x) in resp_g.items()])

    def make_guess_base(self,guesses):
        guess = guesses[0]
        val = self.evaluate(guesses,guess)
        for (i,g) in enumerate(guesses[1:]):
            res = self.evaluate(guesses,g)
            if res<val:
                val = res
                guess = g
        return guess
    #make a guess
    def make_guess(self,guesses):
        return min([(self.evaluate(guesses,g),g) for g in guesses],key=lambda x: x[0])

    def best_guess(self,s):
        if len(s)==1:
            return 1,s[0]
        evals = [(g,self.eval_a_guess(g,s,"")) for g in s]
        g,v= min(evals,key=lambda x:x[1])
        return [x for x,y in evals if y==v],v

    def eval_a_state(self,s,depth="-",pos=(500,500,200,(270/360)*2*math.pi)):
        if len(s)==1:
            self.guess_map[self.enc_state(s)] = s[0]
            return 1,s[:1]
        res,g = min([(1+self.eval_a_guess(gs[0],s,depth+"-"),gs[0]) for v,gs in self.symmetries(s).items()],key=(lambda x:x[0]))
        self.guess_map[self.enc_state(s)] = g
        return res,g 
    
        return 1 + min([self.eval_a_guess(gs[0],s,depth+"-") for v,gs in self.symmetries(s).items()]) 
        items = self.symmetries(s).items()
        iq = []
        ang = lambda x: x/len(items) -0.5
        angs = [1,1,0.5,0.3,0.1,0.1] + [0.1 for i in range(10)]
        for (i,(v,gs)) in enumerate(items):
            new_angle,new_l = pos[3] +angs[len(depth)]*ang(i)*math.pi*2,pos[2]*0.67
            nx,ny = self.t.draw(pos[0],pos[1],new_l,new_angle)
            iq.append( (gs[0],nx,ny,new_l,new_angle))
        
        val = min([self.eval_a_guess(g,s,depth+"-",(nx,ny,nl,na)) for (g,nx,ny,nl,na) in iq])
        #print(depth,val)
        return val
    
    def eval_a_guess(self,g,s,depth="",pos=(500,500,50,0)):
        resp_g = {}
        for code in s:
            resp = self.get_resp(g,code)
            resp_g[resp] = resp_g[resp]+1 if resp in resp_g else 1
        total = len(s)
        return sum([self.eval_a_state(self.reduce(s,g,r),depth,pos)[0]*val/total for (r,val) in resp_g.items()])
    
    def symmetries(self,s):
        syms = {}
        for g in s:
            val = self.evaluate(s,g)
            syms[val] = [g]+(syms[val] if val in syms else [])
        return syms

m = mm_solver()
t = timer().start()
m.populate_resps()
print("populated",t.reset())
s = make_of_length(m.length,m.colours)
big_s = list(s)
_,first_guess = m.eval_a_state(s)
print(t.stop())
total_guesses = 0
for (j,code) in enumerate(s,1):
    current_guess = first_guess
    current_state = list(s)
    for i in range(1,12):
        #guessing
        before = len(current_state)
        resp = m.get_resp(current_guess,code)
        if resp==40:
            break
        current_state = m.reduce(current_state,current_guess,resp)
        #print("current_state:{}, guessing:{}, resp:{},new_state:{}".format(before,current_guess,resp,len(current_state)))
        current_guess = m.guess_map[m.enc_state(current_state)]
    print("n:{}, g:{},avg:{}".format(j,i,total_guesses/j))
    total_guesses +=i
    
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

