# Prism-Cell
PRISM CELL

Built using Python version 3.9.4, and pygame version 2.0.1

Here is a link to python downloads: https://www.python.org/downloads/
Here is a link to instructions on how to install pygame: https://www.pygame.org/wiki/GettingStarted

Short puzzle game made for grade 12 computer science final project. Written using python and pygame, with some custom sprites and stock sound effects.
Little disorganized but having pygame installed and having all the files in one folder, and running Prism Cell.py should launch the game.

Instructions and controls will be shown when the game is opened and should be straightforward. The only information regarding modification of the game,
is that you can create your own custom levels, which have detailed instructions below:



Creating your own level:



It should be noted that level 0 is the title screen, and 1 is the instruction screen, so do try to avoid modifying these files as it may cause issues.

Creating a level is super easy! The level information will be stored as a .txt file in the folder marked "Levels", and the name should be "Level X" with X being an integer. levels must follow one after another numerically (1, 2, 3, etc).

PRISM CELL has many level elements that you can use to create your own levels, such as walls, lasers, recievers (photoresistors), beam-splitting crystals, and refraction prisms. The way these are implemented is through a .txt file.

Formatting for each element is as follows:


Laser:
laser (angle) (colour) (x-coordinate) (y-coordinate) (filename)
Angle is an integer. colour is either WHITE, RED, GREEN, or, BLUE (string). coordinates are integers, and filename is string (Sprites/Laser_diode_(colour).png).

Detector:
detector (colour) (x-coordinate) (y-coordinate) (filename for OFF image) (filename for ON image)
Colour is either WHITE, RED, GREEN, or, BLUE (string). coordinates are integers, and filename is string (Sprites/Photoresistor_(colour)_(OFF, or ON).png).

Splitter:
splitter (x-coordinate) (y-coordinate) (filename)
Coordinates are integers, and filename is string (Sprites/Splitter_Crystal.png).

Refractor:
refractor (x-coordinate) (y-coordinate) (filename)
Coordinates are integers, and filename is string (Sprites/Radial_Refractor.png).

Wall:
wall (x-coordinate) (y-coordinate) (length) (width)
Coordinates, length and width are integers. The coordinates are for the top-left corner of the rectangular wall.

Mirrors:
you must also include a line determining how many mirrors the player is allowed to place per level
mirror (number)
Number is an integer.



You should now be able to create your own level (if you can wrap your head around this confusing implementation)!

There are a few bugs that I was unable to fix before this project was handed in, notably, rarely the laser can pass through a mirror, or travel along its surface. 

