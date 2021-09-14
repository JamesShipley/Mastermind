import pygame,threading,math
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
class tree_drawer:
    def __init__(self,w=1000,h=1000):
        pygame.init()
        self.w,self.h = w,h
        self.gd = pygame.display.set_mode((w,h))
        self.gd.fill(black)
        #threading.Thread(target=self.display,args=()).start()
        self.tick = 1
        
    def display(self):
        pygame.event.get()
        pygame.display.update()

    def draw(self,x,y,length,angle):
        nx,ny = x +length*math.cos(angle),y+length*math.sin(angle)
        pygame.draw.line(self.gd,white if self.tick else red,(x,y),(nx,ny),1)
        pygame.draw.circle(self.gd,red if self.tick else white,(nx,ny),1)
        self.display()
        self.tick = 1 - self.tick
        return nx,ny

