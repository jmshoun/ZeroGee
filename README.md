## ZeroGee

ZeroGee is a space racing game built around 2D inertial physics. Depending on your perspective, you can think of it as "Kerbal Space Program that doesn't require a degree in celestial mechanics", or "Asteroids with a much more boring focus".

### Installation

ZeroGee is developed in Python 3.6 on Linux, but it should run fine on other platforms, provided that you have the right packages installed. You can install the dependencies and launch the game from the command line as follows:

    pip install pygame
    pip install pyyaml
    python ZeroGee.py levels/drag.yaml

The argument to ZeroGee specifies the course to race on, since the in-game menus are nonexistent for the time being.

### Basic Gameplay

At the start of a level, you'll see a splash screen with the word "Ready". Press the space bar, and the text will change to "Set". After the text changes to  "Go", start using your thrusters. Forward thrust is via the up arrow, and left and right thrust is via the left and right arrows, respectively. There is no reverse thrust (you'll have to turn around!).

Fly through all of the gates in the order indicated. The next gate is colored blue, and it will turn green after you have successfully flown through it. After flying through all the gates, fly into the gray finish box and stay there until it turns completely white. If you can stay inside the finish box for five seconds, you will have completed the level. If you leave the finish box, your time will be incremented to include the time inside the finish box, and you will have to re-enter it.

Press the ESCAPE key at any time to exit the game.
