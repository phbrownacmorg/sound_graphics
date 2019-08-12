# Demo of sound_graphics.py
# Peter Brown, 11 Jan 2017

import pygame
from sound_graphics import *
from typing import List

def main(args:List[str]) -> int:
    w:GraphWin = GraphWin('Graphics, now with sound!', 600, 600)
    w.setBackground('lightslategray')
    
    center:Point = Point(300, 300, text='center')
    center.draw(w)
    
    p1:Point = Point(200, 200)
    p2:Point = Point(400, 200)
    line:Line = Line(p1, p2, text='left arrow')
    line.setOutline('orange')
    line.setArrow('first')
    #line.draw(w)
    
    circ:Circle = Circle(p2, 75, text='Blue circle')
    circ.setFill('blue')
    circ.draw(w)
    
    circ2:Circle = Circle(p2, 25, text='This circle is not blue.')
    circ2.setFill('white')
    circ2.draw(w)
    
    rect:Rectangle = Rectangle(center, p2, sound=622.25) #sound=pygame.mixer.Sound('sounds/centered_text.wav'))
    rect.setFill('purple')
    rect.draw(w)
    
    p3:Point = Point(575, 450)
    oval:Oval = Oval(center, p3, sound=pygame.mixer.Sound('sounds/C5-Horn.wav')) # sound=740.0)  #text='green oval')
    oval.setFill('green')
    oval.draw(w)
    
    p5:Point = Point(150, 500)
    line2:Line = Line(p5, center, text='This red line is way too big.')
    line2.setOutline('red')
    line2.draw(w)
    
    poly:Polygon = Polygon(p1, center, p3, sound=880.0) #sound='Pointy triangle')
    poly.draw(w)
    
    p4:Point = Point(300, 550)
    caption:Text = Text(p4, 'Move the mouse to hear the objects. Click to exit.')
    caption.draw(w)
    
    w.getMouse()
    w.close()
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
