# Intelligent Recyclers

## Authors

Diogo Lopes 93700

Gonçalo Mateus 93713

Nuno Estalagem 102245

## Available Files

- ```button.py``` (class responsible for creating the UI buttons)
  

- ```calculations.py``` (contains important calculations used throughout the project, i.e A* search, distance between two positions)
  

- ```macros.py``` (contains some macros used throughout the project like colors, margins and window size)
  

- ```main.py``` (main python file that runs the simulation in loop)


- ```robot.py``` (contains all the classes of the implemented robots)


- ```sector.py``` (class of the sectors that divide the environment)


- ```simulation.py``` (python file that deals with all the UI elements, initialization of other classes and loops for simulating the different architectures)


- ```tile.py``` (class of the different tiles that generate the environment)


- ```trash.py``` (class of the trash that is spawned in the environment)


## Run

There are 2 available ways of running the project:

- executable Ubuntu file (ubuntuMain -> ```./ubuntuMain```, if permission denied -> ```chmod 775 ubuntuMain```)


- executable Windows file (windowsMain.exe -> ```.\windowsMain.exe```)


- running the main file in the command line by using the command ```main.py```


If successfully running, the user should be prompted with the following pygame window:

![](https://cdn.discordapp.com/attachments/829496008815280128/987422098601439333/unknown.png)

From this UI the available simulation architectures are:

- **Random Collectors** (3 collectors move randomly)


- **Reactive Collectors** (3 collectors with FOV reactions)


- **Intelligent Collectors** (2 detectors sweep each one half of the environment and 3 collectors cooperate collecting and delivering trash to the containers)


- **Sector Prototype** (2 detectors sweep sectors where they believe is more trash and same collectors as previous architecture)
