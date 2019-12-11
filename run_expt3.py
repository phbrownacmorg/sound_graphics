import graphics as g
from sound_graphics import *
import time
from datetime import datetime
import math
import random
import sys
from typing import Any, List, Tuple

# Code to run the experiment

num_observers = 13
conditions = ["mouse", "tablet"]

# TO BE FILLED IN: this should be a list of locations.  Each location should
# be specified by its coordinates (which can be a Tuple[float, float]).
locations:List[Tuple[float, float]] = [(0.5, 0.5), (-0.5, -1), (1, -0.5),
                                       (0, 0), (-1, 1)] 

shape = ['circle', 'rectangle']

# TO BE FILLED IN: this should be a list of sizes.  Sizes can be specified as
# areas or as circle radii.  If you choose areas, you'll need to convert the
# areas to radii when you make circles, and if you choose radii, you'll need to
# convert those radii to areas (pi * radius**2) to make triangles.  Your choice.
sizes:List[float] = [1, 1.5, 2]

# Create the trial sequences

# trials[0] remains as an empty list, because there's no observer 0
trials:List[Any] = [[]] 

# Make a sublist for each observer in the interval [1, num_observers]
for i in range(1, num_observers + 1):  
    trials.append([])

    # Within each observer's list, a sublist for each condition
    for c in conditions:
        trials[i].append([])  # Becomes trials[i][c]

        # Fill in the list for each condition.  Each trial should specify a
        # location, shape, and size.  Naturally, what you actually generate
        # should use indices into the lists of locations, shapes, and sizes
        # above.  How exactly you store those values in this list--whether you
        # store indices or actual values--is up to you.

        # Make sure what you put here is consistent with the way the trial is
        # unpacked and used in run_trial.  (Alternatively, you could change
        # run_trial to match what's here.)
        
        # FILL IN

        for j in range(2): # 2 practice trials
            t = {} # Empty dictionary for the trial
            t['shape'] = shape[1 - j] # Do the triangle first
            t['size'] = sizes[1] # Intermediate size
            t['point'] = locations[-2 + j] # Taken from locations[-2:]
            trials[i][conditions.index(c)].append(t)

        # All possible combinations of size, shape, and location
        num_sizes = len(sizes) - 1
        num_locations = 2
        num_shapes = len(shape)
        num_trials = num_sizes * num_locations * num_shapes
        combos = list(range(num_trials)) 
        random.shuffle(combos) # Randomize the order
        for j in range(num_trials): # Experimental trials
            t = {}
            # Shape is all circles for the low-numbered combos and
            #  all the other shape for the high-numbered trials
            t['shape'] = shape[combos[j] // (num_sizes * num_locations)]
            # Size is sizes[0] for even combos, sizes[2] for odd combos
            t['size'] = sizes[2 * (combos[j] % num_sizes)]
            # Point is drawn from the first locations
            t['point'] = locations[(combos[j] % num_shapes) // num_locations]
            trials[i][conditions.index(c)].append(t)

def run_trial(trial, outfile, observer, condition, w):
    """Run a trial, using the trial specification in TRIAL and recording
    the results (including the observer and condition) in OUTFILE."""
    # This function is substantially complete
    
    # Create and draw the figure
    figure = None
    orientation = None
    
    if trial['shape'] == 'circle':
        figure = Circle(g.Point(trial['point'][0], trial['point'][1]),
                        trial['size'], pygame.mixer.Sound('sounds/C3-cello.5s.ogg'))
    elif trial['shape'] == 'rectangle':
        # Actually the square root of the ratio of the sides
        eccentricity = 1.65 
        side = math.sqrt(math.pi) * trial['size']
        hside = side * eccentricity
        vside = side / eccentricity
        orientation = Polygon.RIGHT
        if abs(trial['point'][0]) > abs(trial['point'][1]):
            orientation = Polygon.UP
            hside = side / eccentricity
            vside = side * eccentricity
        p1 = g.Point(trial['point'][0]-(hside/2), trial['point'][1]-(vside/2))
        p2 = g.Point(trial['point'][0]+(hside/2), trial['point'][1]+(vside/2))
        figure = Rectangle(p1, p2, pygame.mixer.Sound('sounds/C3-cello.5s.ogg'))
                    
    figure.draw(w)

    # Run the actual trial
    start_time = datetime.now()
    key = w.getKey()
    end_time = datetime.now()

    # Record the results and clean up
    figure.undraw()

    # Stop the sound, so the user knows there's been a change
    w.itemchannel.stop();
    w.itemsound = None;
    
    if key == 'space':
        choice = 'circle'
    else:
        choice = shape[1]
    
    outfile.write(str(observer) + ',' + condition + ',' + trial['shape'] + ','
                  + str(trial['point']) + ',' + str(trial['size']) + ','
                  + str(orientation) + ',' + str(start_time) + ','
                  + str(end_time) + ',' + choice + '\n') 

def getLikert(msg):
    return int(input(msg))
    
def run_trial_set(observer:int, condition:str) -> None:
    """Run the trials for observer number OBSERVER in condition CONDITION,
    recording results as we go."""
    # This function is substantially complete
    w = GraphWin('sound_graphics experiment', 700, 700)
    w.setCoords(-4, -4, 4, 4)
    w.setBackground('white')
    
    with open('obs'+str(observer)+'-'+condition+'.csv', 'a') as outfile:
        for t in trials[observer][conditions.index(condition)]:
            run_trial(t, outfile, observer, condition, w)
        w.close()
        conf = getLikert('On a scale of 1 to 5, how confident are you in '
                         + 'your answers?\n1 = totally guessing, 5 = total '
                         + 'confidence: ')
        ease = getLikert('On a scale of 1 to 5, how easy did you find the task?'
                         + '\n1 = really hard, 5 = really easy: ')
        outfile.write('Confidence,' + str(conf) + ',Ease,' + str(ease) + '\n')
            
def main(args: List[str]) -> int:
    # Set the observer number and the experimental condition.  This function
    # is probably about complete.
    observer = int(input('Please enter the observer number: '))
    
    cond_code = input('Is this trial set using the mouse (m) or tablet (t)? ')
    cond_code = cond_code.strip().lower()
    condition = ''
    if cond_code.startswith('m'):
        condition = 'mouse'
    elif cond_code.startswith('t'):
        condition = 'tablet'
    run_trial_set(observer, condition)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
