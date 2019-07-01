# sound_graphics
Adds sonification to John Zelle's graphics.py library

This is a project to add sound output to [John Zelle's](https://mcsp.wartburg.edu/zelle/) library
[graphics.py](https://mcsp.wartburg.edu/zelle/python/graphics.py),
making that library at least marginally accessible to visually-impaired programmers.

## Usage

  1.  Put Zelle's `graphics.py` into the folder where you will develop your Python code.
      - Alternate method, if you want your development code more separate: install graphics.py with `pip install graphics.py`
  2.  Unzip the contents of this repository into the directory where you will develop your Python code.
  3.  In your Python code, where you would normally put `import graphics`, put `import sound_graphics` instead.
  
The objects in `sound_graphics` take the same arguments as the objects with the same names in `graphics.py`.  In addition,
the `sound_graphics` objects take further, optional arguments to control the sonification.
