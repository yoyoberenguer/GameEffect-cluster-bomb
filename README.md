
# Game Effect - cluster bomb 

Add explosions effect to your video game using the source code provided into this git page

Please have also a look at the cython version to explore the same algorithm improved with 
cython (FPS > 300)

## Python version 
```
Run the program ClusterBomb.py in your favorite python IDE 
Requirement: 
- Numpy
- Python 3
- Pygame

C:\>pip install pygame==2.0, numpy==1.19.3
```

## Cython version x10 faster

```
Two tests version :

1) ClusterMain_Collision.py 
   This version include lines of code to detect collision with background 
   layer (or object(s) belonging to a specific layer).
   The cluster bomb will explose only if it touch a solid ground.
   
2) ClusterMain_NoCollision.py
   Version without background collision detection, bombs explose regardless of the 
   background image (fastest version).
   Bombs and background can be converted for fast blit (FPS over 100FPS).
```
Requirment :

```
C:\>pip install cython, matplotlib, pygame==2.0, numpy==1.19.3 

- python > 3.0
- numpy==1.19.3
- pygame
- Cython
- A C compiler for windows (Visual Studio, MinGW etc) install on your system 
  and linked to your windows environment.
  Note that some adjustment might be needed once a compiler is install on your system, 
  refer to external documentation or tutorial in order to setup this process.
  e.g https://devblogs.microsoft.com/python/unable-to-find-vcvarsall-bat/
```

Compilation : 
```
In a command prompt and under the directory containing the source files
C:\>python setup_Project.py build_ext --inplace

If the compilation fail, refers to the requirement section and make sure cython 
and a C-compiler are correctly install on your system. 

```


![alt text](https://github.com/yoyoberenguer/GameEffect/blob/master/Screendump0.png)
![alt text](https://github.com/yoyoberenguer/GameEffect/blob/master/Screendump1.png)
![alt text](https://github.com/yoyoberenguer/GameEffect/blob/master/Screendump2.png)

