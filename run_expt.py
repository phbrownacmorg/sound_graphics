import sys
from typing import Any, List, Tuple

# Code to run the experiment

num_observers = 13
conditions = ["mouse", "tablet"]

# TO BE FILLED IN: this should be a list of locations.  Each location should
# be specified by its coordinates (which can be a Tuple[float, float]).
locations:List[Tuple[float, float]] = [] 

shape = ['circle', 'triangle']

# TO BE FILLED IN: this should be a list of sizes.  Sizes can be specified as
# areas or as circle radii.  If you choose areas, you'll need to convert the
# areas to radii when you make circles, and if you choose radii, you'll need to
# convert those radii to areas (pi * radius**2) to make triangles.  Your choice.
sizes:List[float] = []

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

        # FILL IN
        

def run_trial(trial, outfile, observer, condition):
    """Run a trial, using the trial specification in TRIAL and recording
    the results (including the observer and condition) in OUTFILE."""
        
    # FILL IN

    
def run_trial_set(observer:int, condition:str) -> None:
    """Run the trials for observer number OBSERVER in condition CONDITION,
    recording results as we go."""
    # This function is probably complete.
    with open('obs'+str(observer)+'-'+condition+'.csv', 'a') as outfile:
        for t in trials[observer][condition]:
            run_trial(t, outfile, observer, condition)

def main(args: List[str]) -> int:
    # Set the observer number and the experimental condition.  This function
    # is probably about complete.
    observer = int(input('Please enter the observer number:'))
    
    cond_code = input('Is this trial set using the mouse (m) or tablet (t)?')
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
