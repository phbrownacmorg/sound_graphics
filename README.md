# sound_graphics
Adds sonification to John Zelle's graphics.py library

This is a project to add sound output to [John Zelle's](https://mcsp.wartburg.edu/zelle/) library
[graphics.py](https://mcsp.wartburg.edu/zelle/python/graphics.py),
making that library at least marginally accessible to visually-impaired programmers.

## Dependencies

(Also FFMpeg!)

This library works only on Python 3.  It requires the following other libraries to be installed where Python can find them.  This is best done using `pip install`.  All the libraries are available on [PyPI](https://pypi.org/).

  * [gTTS](https://github.com/pndurette/gTTS)
  * [pygame](https://www.pygame.org/)
  * [numpy](https://www.numpy.org/)
  * [graphics.py](https://mcsp.wartburg.edu/zelle/python/graphics.py) (yes, this is [on PyPI](https://pypi.org/project/graphics.py/))

## Usage

  1.  Unzip the contents of this repository into the directory where you will develop your Python code.
  2.  In your Python code, where you would normally put `import graphics`, put `import sound_graphics` instead.
  
The objects in `sound_graphics` take the same arguments as the objects with the same names in `graphics.py`.  In addition,
the `sound_graphics` objects take further, optional arguments to control the sonification.
