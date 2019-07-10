# Zelle's graphics.py with added sounds
# Peter Brown <phbrown@acm.org>, 2017-01-07

import graphics as g
from gtts import gTTS
import math
import os
import numbers
import numpy as np
import pygame
import pygame.mixer
import pygame.sndarray
import string
import subprocess
import sys
from tkinter import Event
from typing import Optional, List, Tuple, Union
#import pyttsx

class GraphWin(g.GraphWin):
    """Graphics window with additional sound.  The sound follows the
    scheme laid out in Javier Sanchez, "Identifying and communicating 2D
    shapes using auditory feedback," in _Proceedings of the International
    Conference on Auditory Display, ICAD 2010_, pp. 89-95, Washington, DC, 
    USA, June 9-15, 2010."""

    def __init__(self, title:str = "Graphics Window", width:int = 200,
                 height:int = 200, autoflush:bool = True) -> None:
        super().__init__(title, width, height, autoflush)
        #pygame.mixer.pre_init(frequency=44100)
        pygame.init()
        self.bind("<Motion>", self._onMouseMove)
        self.bind("<Enter>", self._onEnter)
        self.bind("<Leave>", self._onLeave)
        
        # Generate static programmatically
        noise = np.random.normal(0, 0.05, Tone.SAMPLE_RATE * 3)
        noise = Tone.MAX_SAMPLE * noise
        stereo = np.resize(noise, (len(noise), 2))
        self.bgsound = pygame.sndarray.make_sound(np.asarray(stereo, dtype=np.int16))
        #self.bgsound = pygame.mixer.Sound(file='sounds/bgstatic.wav')
        self.bgchannel = pygame.mixer.Channel(0)
        
        self.itemchannel = pygame.mixer.Channel(1)
        self.mousechannel = pygame.mixer.Channel(2)
        pygame.mixer.set_reserved(3)
        self.bgchannel.play(self.bgsound, loops=-1)
        self.bgchannel.set_volume(0)


    def getPropPt(self, x:float, y:float, screen:bool = False) -> Tuple[float, float]:
        if screen == False:
            x,y = self.toScreen(x, y)
        # Transform to a proportion of the height/width
        x /= self.getWidth()
        y /= self.getHeight()
        return x, y

    def _playSoundInside(self, Xprop:float, sound:pygame.mixer.Sound, 
            loops:int) -> None:
        self.mousechannel.set_volume(0)
        self.bgchannel.set_volume(0)
        if self.itemchannel.get_sound() != sound:
            self.itemchannel.stop()
            #self.ttsengine.say('Engine')
            #self.ttsengine.runAndWait()
            self.itemchannel.play(sound, loops)
        self.itemchannel.set_volume((1 - Xprop), Xprop)

    def _playSoundNear(self, Xprop:float, sound:pygame.mixer.Sound, 
            loops:int) -> None:
        self.mousechannel.set_volume(0.1 * (1 - Xprop), 0.1 * Xprop)
        self.bgchannel.set_volume(0.1 * (1 - Xprop), 0.1 * Xprop)
        if self.itemchannel.get_sound() != sound:
            self.itemchannel.stop()
            self.itemchannel.play(sound, loops)
        self.itemchannel.set_volume(0.3 * (1 - Xprop), 0.3 * Xprop)

    def _playSoundOutside(self, Xprop:float) -> None:
        self.mousechannel.set_volume(0.1 * (1 - Xprop), 0.1 * Xprop)
        self.bgchannel.set_volume(0.5 * (1 - Xprop), 0.5 * Xprop)
        self.itemchannel.stop()

    def _onEnter(self, e:Event) -> None:
        self.bgchannel.play(self.bgsound, loops=-1)

    def _onLeave(self, e:Event) -> None:
        self.bgchannel.stop()
        self.itemchannel.stop()
        self.mousechannel.stop()

    def _onMouseMove(self, e:Event) -> None:
        #print(e.x, e.y, self.toWorld(e.x, e.y), end=': ')
        
        Xprop, Yprop = self.getPropPt(e.x, e.y, True) # type: ignore
        # Iterate over self.items from back to front, checking if the mouse
        # is over any of the items with sound
        insideItem = None
        nearItem = None
        for item in reversed(self.items):
            if hasattr(item, 'hasSound') and item.hasSound(): # type: ignore
                #x, y = self.toWorld(e.x, e.y)
                assert isinstance(item, SoundObject)
                contains = item.containsPt(e.x, e.y) # type: ignore
                #print(contains, end=' ')
                if contains == SoundObject.INSIDE:
                    insideItem = item
                    break
                elif (contains == SoundObject.NEAR
                      and nearItem == None):
                    nearItem = item
        #print()
        mousesound = Tone(1 - Yprop).getSound()
        self.mousechannel.play(mousesound, loops = -1)
        if insideItem is not None:
            self._playSoundInside(Xprop, insideItem.sound(), insideItem.loops())
        elif nearItem is not None:
            self._playSoundNear(Xprop, nearItem.sound(), nearItem.loops())
        else:
            self._playSoundOutside(Xprop)
            
    def close(self) -> None:
        super().close()
        pygame.quit()

class Tone(object):
    # Minimum and maximum frequencies in Hz
    MIN_FREQ = 60
    LOG_MIN_FREQ = math.log(MIN_FREQ)
    MAX_FREQ = 1200
    LOG_MAX_FREQ = math.log(MAX_FREQ)
    SAMPLE_RATE = 22050
    MAX_SAMPLE = 2 ** 15 - 1 # maximum value for any sample

    def __init__(self, y: float) -> None:
        """Y is a number between 0 and 1, indicating the pitch as a
        geometric interpolation between MIN_FREQ and MAX_FREQ."""
        # Clamp y to prevent seg-faulting
        if y < 0 or y > 1:
            freq:float = Tone.MAX_FREQ * 4
        else:
            freq = math.exp((1 - y) * Tone.LOG_MIN_FREQ + y * Tone.LOG_MAX_FREQ)
    
        # I want enough samples for 1 full cycle of the tone
        length:float = Tone.SAMPLE_RATE / freq
        omega:float = 2 * np.pi / length
        xvalues = np.arange(int(length)) * omega
        #print(np.obj2sctype(xvalues))
        samples = Tone.MAX_SAMPLE * np.sin(xvalues)
        stereo = np.resize(samples, (len(samples), 2))
        self.sound:pygame.mixer.Sound = \
            pygame.sndarray.make_sound(np.asarray(stereo, dtype=np.int16))

    def getSound(self) -> pygame.mixer.Sound:
        return self.sound
        

class SoundObject(g.GraphicsObject):
    def __init__(self, 
                 sound:Union[pygame.mixer.Sound,str,float,None]=None,
                 text:Optional[str]=None) -> None:
        self._sound:Optional[pygame.mixer.Sound] = None

        # Backwards compatibility
        if sound == None and text != None:
            sound = text

        if sound != None:
            if hasattr(sound, 'play'): # sound is a Sound
                self._sound = sound
                self._loops:int = 0
            elif isinstance(sound, str): #sound is a string
                if len(sound) > 0:
                    self._sound = self.textToSpeech(sound)
                    self._loops = 0
            elif isinstance(sound, float):
                # Make a tone out of it
                y:float = sound
                self._sound = Tone(y).getSound()
                self._loops = -1

    @staticmethod
    def textToFilename(text:str) -> str:
        result = text.strip().casefold().replace(' ', '_')
        keepchars = string.ascii_lowercase + string.digits + '_'
        result = ''.join(c for c in result if c in keepchars)
        return result

    @staticmethod
    def makeWavTTS(textarg:str, fname:str) -> None:
        wavname = os.path.join('sounds', fname + '.wav')
        mp3name = os.path.join('sounds', fname + '.mp3')
        tts = gTTS(text=textarg, lang='en')
        tts.save(mp3name)
        ffmpegExe = 'ffmpeg'
        if sys.platform == 'win32':
            ffmpegExe = os.path.join('..','ffmpeg','bin','ffmpeg.exe')
        subprocess.run([ffmpegExe, '-i', mp3name, wavname])
        os.remove(mp3name)

    @staticmethod
    def textToSpeech(text:str) -> pygame.mixer.Sound:
        fname = SoundObject.textToFilename(text)
        #print(fname)
        wavname = os.path.join('sounds', fname + '.wav')
        print(wavname)
        # If the WAV file doesn't exist already, create it
        if not os.path.isfile(wavname):
            print('WAV does not exist.')
            SoundObject.makeWavTTS(text, fname)
        return pygame.mixer.Sound(wavname)

    @staticmethod
    def distanceL2(x1:float, y1:float, x2:float, y2:float) -> float:
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        
    @staticmethod
    def dot(x1:float, y1:float, x2:float, y2:float) -> float:
        """2-D dot product."""
        return x1*x2 + y1*y2

    # Size of the "near" fringe around the outside of the object, in
    # pixels
    FRINGE = 30

    OUTSIDE = 0
    INSIDE = 1
    NEAR = -1

    def scaleX(self, x:float) -> float:
        result = x
        if self.canvas and not self.canvas.isClosed() and self.canvas.trans:
            result /= self.canvas.trans.xscale
        return result

    def scaleY(self, y:float) -> float:
        result = y
        if self.canvas and not self.canvas.isClosed() and self.canvas.trans:
            result /= self.canvas.trans.yscale
        return result
        
    def ptToScreenTuple(self, pt:g.Point) -> Tuple[int, int]:
        x = pt.getX()
        y = pt.getY()
        if self.canvas and not self.canvas.isClosed() and self.canvas.trans:
            x,y = self.canvas.toScreen(x, y)
        return int(x),int(y)
    
    # Note that the final containsPt and distance calculation must be in screen space!  
    # Only in screen space can the fringe be expected to be the same in X and Y.  (The Circle
    # is a special case because anisotropic scaling can do oddball things to the radius, but if 
    # the X and Y scalings differ by much a Circle won't be circular anyway.)

    def boxContains(self, centerPt:g.Point, width:float, height:float, 
                    x:float, y:float) -> int:
        """Determine whether the point (x, y) is contained within the box
        centered at centerPt and width x height in size.  NOTE: This function
        assumes that x and y are in screen space and centerPt, width, and height
        are in world space."""
        cx,cy = self.ptToScreenTuple(centerPt)
        width = self.scaleX(width)
        height = self.scaleY(height)
        
        dx = abs(cx - x)
        dy = abs(cy - y)
        halfwidth = width/2
        halfheight = height/2
        #print(cx, cy, width, height, ':')
        if dx <= halfwidth and dy <= halfheight:
            result = SoundObject.INSIDE
        elif dx <= (halfwidth+SoundObject.FRINGE) and dy <= (halfheight+SoundObject.FRINGE):
            result = SoundObject.NEAR
        else:
            result = SoundObject.OUTSIDE
        return result

    def bBoxContains(self, x:float, y:float) -> int:
        """Determine whether the point(x, y) is contained within the box
        defined by p1 and p2.  x and y are in screen space."""
        # p1 and p2 are in world space
        p1 = self.getP1() #  type: ignore
        p2 = self.getP2() #  type: ignore
        width = abs(p1.getX() - p2.getX()) # World space
        height = abs(p1.getY() - p2.getY()) #World space
        centerPt = g.Point((p1.getX() + p2.getX())/2, (p1.getY() + p2.getY())/2)
        return self.boxContains(centerPt, width, height, x, y)

    def distToLineSeg(self, x:float, y:float, p1:g.Point, p2:g.Point) -> float:
        """Finds the distance in screen space from the point (x, y) to the line p1-p2,
        by projecting (x, y) onto the line."""
        # Convert p1, p2 to screen coordinates and make the vectors
        assert self.canvas is not None
        scr_p1 = pygame.math.Vector2(self.canvas.toScreen(p1.getX(), p1.getY()))
        scr_p2 = pygame.math.Vector2(self.canvas.toScreen(p2.getX(), p2.getY()))
        p1p2 = scr_p2 - scr_p1
        p2p1 = scr_p1 - scr_p2

        p = pygame.math.Vector2(x, y)
        p1p = p - scr_p1
        p2p = p - scr_p2
        # If (x, y) is behind p1, distance is distance to p1
        if p1p.dot(p1p2) < 0:
            d = scr_p1.distance_to(p)
        elif p2p.dot(p2p1) < 0: # p2 is closest
            d = scr_p2.distance_to(p)
        # Else, project p onto line
        else:
            # Strang's approach: naah
            #   p1p2sqr = p1p2.length_squared()
            #   d = math.sqrt((p1p.length_squared() * p1p2sqr - p1p2.dot(p1p)**2)/p1p2sqr)
            # lbackstrom: https://www.topcoder.com/community/data-science/data-science-tutorials/geometry-concepts-basic-concepts
            d = abs(p1p2.cross(p1p)/p1p2.length())
        return d

    def hasSound(self) -> bool:
        return self._sound != None

    def sound(self) -> Optional[pygame.mixer.Sound]:
        return self._sound
        
    def loops(self) -> int:
        return self._loops

    def containsPt(self, x:float, y:float) -> int:
        """Returns 1 if the point x,y is contained in this object, -1
        if the point x,y is within FRINGE pixels of this object, 
        or 0 if the point is farther from the object.  Subclasses should
        override this method."""
        return SoundObject.OUTSIDE
        
class Point(SoundObject, g.Point):
    def __init__(self, x:float, y:float, 
                 sound:Union[pygame.mixer.Sound,str,float,None] = None, 
                 text:Optional[str] = None) -> None:
        SoundObject.__init__(self, sound, text)
        g.Point.__init__(self, x, y)

    def containsPt(self, x:float, y:float) -> int:
        return self.boxContains(self, 0, 0, x, y)


class Line(SoundObject, g.Line):
    def __init__(self, p1:g.Point, p2:g.Point, 
                 sound:Union[pygame.mixer.Sound,str,float,None] = None,
                 text:Optional[str] = None) -> None:
        SoundObject.__init__(self, sound, text)
        g.Line.__init__(self, p1, p2)
        
    def containsPt(self, x:float, y:float) -> int:
        """Finds the distance from the point (x, y) to this line, by projecting
        (x, y) onto the line."""
        d = self.distToLineSeg(x, y, self.getP1(), self.getP2())
        result = SoundObject.OUTSIDE
        if d == 0:
            result = SoundObject.INSIDE
        elif d < SoundObject.FRINGE:
            result = SoundObject.NEAR
        # print(scr_p1, scr_p2, p, p1p.dot(p1p2), p1p.angle_to(p1p2), p2p.dot(p2p1), p2p.angle_to(p2p1), d, result)
        return result

class Circle(SoundObject, g.Circle):
    def __init__(self, center:g.Point, radius:float, 
                 sound:Union[pygame.mixer.Sound,str,float,None]=None,
                 text:Optional[str]=None) -> None:
        SoundObject.__init__(self, sound, text)
        g.Circle.__init__(self, center, radius)

    def containsPt(self, x:float, y:float) -> int:
        result = SoundObject.OUTSIDE
        cx,cy = self.ptToScreenTuple(self.getCenter())
        # if we're drawing circles, xscale and yscale better be similar
        r = self.scaleX(self.getRadius())
        outside = self.distanceL2(x, y, cx, cy) - r
        if outside <= 0:
            result = SoundObject.INSIDE
        elif outside <= SoundObject.FRINGE:
            result = SoundObject.NEAR
        return result

class Rectangle(SoundObject, g.Rectangle):
    def __init__(self, p1:g.Point, p2:g.Point, 
                 sound:Union[pygame.mixer.Sound,str,float,None] = None,
                 text:Optional[str] = None) -> None:
        SoundObject.__init__(self, sound, text)
        g.Rectangle.__init__(self, p1, p2)

    def containsPt(self, x:float, y:float) -> int:
        return self.bBoxContains(x, y)

# TODO: Fix containsPt
class Oval(SoundObject, g.Oval):
    def __init__(self, p1:g.Point, p2:g.Point, 
                 sound:Union[pygame.mixer.Sound,str,float,None] = None,
                 text:Optional[str] = None) -> None:
        SoundObject.__init__(self, sound, text)
        g.Oval.__init__(self, p1, p2)
        self._xr = abs(p1.getX() - p2.getX())/2
        self._yr = abs(p1.getY() - p2.getY())/2

    def containsPt(self, x:float, y:float) -> int:
        # Should really be more precise
        result = self.bBoxContains(x, y)
        # If result is OUTSIDE or NEAR, use it.
        # If result is INSIDE, refine it.
        if result == SoundObject.INSIDE:
            cx,cy = self.ptToScreenTuple(self.getCenter())
            xr = self.scaleX(self._xr)
            yr = self.scaleY(self._yr)
            k = (x - cx)**2/xr**2 + (y - cy)**2/yr**2
            if k > 1:
                result = SoundObject.NEAR
            # Otherwise, result is already INSIDE
        return result

#TODO: Figure out containment from the start
class Polygon(SoundObject, g.Polygon):
    def __init__(self, *points,
                 sound:Union[pygame.mixer.Sound,str,float,None] = None,
                 text:Optional[str] = None) -> None:
        SoundObject.__init__(self, sound, text)
        g.Polygon.__init__(self, list(points))

    def containsPt(self, x:float, y:float) -> int:
        result:int = SoundObject.OUTSIDE
        # Is it INSIDE?
        ## Intersect each line segment with the ray from (x, y) to +x
        intersections:int = 0
        for i in range(len(self.points)):
            start:g.Point = self.points[i]
            end:g.Point = self.points[(i+1) % len(self.points)]
            if ((start.y - y) * (end.y - y) <= 0) \
                and (start.x >= x or end.x >= x) \
                and ((start.x + (((y - start.y)*(end.x - start.x))/(end.y - start.y))) \
                      >= x):
                intersections += 1
        if (intersections % 2) == 1: # Odd number of intersections
            result = SoundObject.INSIDE
        else:        
            # Is it NEAR?
            mindist:float = self.distToLineSeg(x, y, self.points[-1], 
                                                self.points[0])
            for i in range(len(self.points)-1):
                dist:float = self.distToLineSeg(x, y, self.points[i], self.points[i+1])
                mindist = min(mindist, dist)
            if mindist < SoundObject.FRINGE:
                result = SoundObject.NEAR
        # Otherwise, it's OUTSIDE
        return result

class Text(SoundObject, g.Text):
    def __init__(self, p:g.Point, text:str, 
                sound:Union[pygame.mixer.Sound,str,float,None]=None, 
                updateSound:bool=False) -> None:
        SoundObject.__init__(self, sound, text)
        g.Text.__init__(self, p, text)
        print()
        self._updateSound = updateSound

#   def setText(self, newtext):
#       g.Text.setText(self, newtext)
#       if self._updateSound and len(newtext) > 0:
#           self._sound = self.textToSpeech(newtext)

    def containsPt(self, x:float, y:float) -> int:
        # Total wild guess at the dimensions.
        # With access to the font, I *can* do better
        width:float = 100
        height:float = 30
        # Convert dims to world space, so boxContains can convert them back
        if self.canvas and not self.canvas.isClosed() and self.canvas.trans:
            xfm = self.canvas.trans
            width *= xfm.xscale
            height *= xfm.yscale
        return self.boxContains(self.getAnchor(), width, height, x, y)

# TODO: implement
class Entry(g.Entry):
    pass

class Image(SoundObject, g.Image):
    def __init__(self, p:g.Point, filename:str, 
                sound:Union[pygame.mixer.Sound,str,float,None] = None,
                text:Optional[str] = None) -> None:
        SoundObject.__init__(self, sound, text)
        g.Image.__init__(self, p, filename)

    def containsPt(self, x:float, y:float) -> int:
        return self.boxContains(self.getAnchor(), self.getWidth(), 
                self.getHeight(), x, y)

def color_rgb(r:int, green:int, b:int) -> str:
    return g.color_rgb(r, green, b)

def update(rate:Optional[float]=None) -> None:
    g.update()

def test() -> None:
    win = GraphWin()
    win.setCoords(0,0,10,10)
    t = Text(g.Point(5,5), "Centered Text")
    t.draw(win)
    p = Polygon(g.Point(1,1), g.Point(5,3), g.Point(2,7), sound='Polygon')
    p.draw(win)
    e = Entry(g.Point(5,6), 10)
    e.draw(win)
    win.getMouse()
    p.setFill("red")
    p.setOutline("blue")
    p.setWidth(2)
    s = ""
    for pt in p.getPoints():
        s = s + "(%0.1f,%0.1f) " % (pt.getX(), pt.getY())
    t.setText(e.getText())
    e.setFill("green")
    e.setText("Spam!")
    e.move(2,0)
    win.getMouse()
    p.move(2,3)
    s = ""
    for pt in p.getPoints():
        s = s + "(%0.1f,%0.1f) " % (pt.getX(), pt.getY())
    t.setText(s)
    win.getMouse()
    p.undraw()
    e.undraw()
    t.setStyle("bold")
    win.getMouse()
    t.setStyle("normal")
    win.getMouse()
    t.setStyle("italic")
    win.getMouse()
    t.setStyle("bold italic")
    win.getMouse()
    t.setSize(14)
    win.getMouse()
    t.setFace("arial")
    t.setSize(20)
    win.getMouse()
    win.close()
    pygame.quit()

#MacOS fix 2
#tk.Toplevel(_root).destroy()

# MacOS fix 1
update()

if __name__ == "__main__":
    test()
