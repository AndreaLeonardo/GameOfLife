# GameOfLife
## A Simple GUI for the Game Of Life Simulation made with PyQt5

This program was made as a programming assignment for the Human Computer Interaction course.

This program allows the user to simulate John Conway's "Game of Life". It is based on a large table (50x64 in our case)
in which each box can be populated (colored) or not. When the game begins, each box in the table decides
the next stage according to the rules applied and the current status of the neighbors (the 8 adjacent squares).

The rules applied can be expressed in a simple way through a string of the type "B ... / S ..." 
where instead of the dots there are numbers that indicate how many neighbors must be alive for the current box 
to be born or survive (in all other cases the box dies). The program contains 4 possible rules 
(they can be chosen from the selector at the top above the table):

- Normal B2 / S23
- HighLife B36 / S23
- Day-Night B3678 / S34678
- Bosco B34-45 / S33-57

For the Bosco's Rule we consider the neighbors in an 11x11 square.

<img width="791" alt="Schermata 2022-05-10 alle 12 02 28" src="https://user-images.githubusercontent.com/48476092/167603827-f5b50fa7-e76a-44fa-b9ef-ad7085ab0733.png">

Below the table we have the control panel where you can:

- start the game or pause it with the "Start! / Pause!"
- refresh the table with the "Refresh" button
- Empty the table with the "Empty" button
- load a pattern in .txt format with the button with the floppy disk (the pattern is saved and can be reused later)
- use a previously saved pattern with the button with the magnifying glass
- zoom with the dial
- change the framerate with the glider
- switch from dark to light version or vice versa
- activate secondary options such as: display the color of living cells (depending on age),
  allow the cells at the edges to consider the cells on the opposite side as neighbors, or display the simulation info (births, deaths and generations)


