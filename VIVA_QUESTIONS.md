# Viva Preparation — Smart Traffic Intersection Simulator

## Project summary

This project simulates a four-approach traffic intersection using Python and Pygame. It demonstrates 2D drawing primitives, translation, time-based animation, keyboard event handling, a traffic-light state machine, lane queues and basic vehicle-spacing logic.

## Common viva questions and answers

### 1. What is the objective of this project?
To demonstrate fundamental 2D Computer Graphics concepts through an animated traffic intersection in which vehicles respond to signal phases.

### 2. What is Pygame?
Pygame is a Python library for multimedia applications, including 2D drawing, animation, keyboard input and game development.

### 3. Which graphics primitives are used?
Rectangles, circles, lines and rounded rectangles. The car body, windows, wheels, buildings, road markings and lamps are composed from these primitives.

### 4. What is translation?
Translation moves an object by changing its coordinates. If a car is at position `(x, y)`, horizontal movement changes `x` while `y` remains constant; vertical movement changes `y` while `x` remains constant.

### 5. How is animation produced?
The program repeatedly handles events, updates object positions, draws the updated scene and refreshes the display. The sequence of frames creates the illusion of motion.

### 6. Why use delta time (`dt`)?
`dt` is the elapsed time since the prior frame. Moving by `speed * dt` makes vehicle speed depend on elapsed time rather than directly on how many frames the computer renders.

### 7. What does `pygame.time.Clock().tick(FPS)` do?
It limits the loop to the target frame rate and returns elapsed time in milliseconds. The code converts that value to seconds for movement and timers.

### 8. What is a state machine in this project?
The traffic controller has a finite set of named states such as `H_GREEN`, `H_YELLOW`, `V_GREEN`, `V_YELLOW` and `ALL_RED`. Time or user input causes transitions between those states.

### 9. Why is there an all-red clearance phase?
It gives vehicles already in the intersection time to clear before the perpendicular direction receives green. It is a simplified safety measure in this educational simulation.

### 10. How does a car stop at a red signal?
Each lane has a stop-line coordinate. When its group is not green, movement is clamped at the stop position if the vehicle has not crossed the line yet. Vehicles already past the line are allowed to clear the intersection.

### 11. How are vehicles kept from overlapping in a lane?
Vehicles are processed from front to back. A following car's proposed position is limited so it stays at least the vehicle length plus a fixed gap behind the leading car.

### 12. How are horizontal and vertical vehicles represented?
Each lane has an axis (`x` or `y`), a direction (`+1` or `-1`), a fixed lane coordinate and a signal group. Those properties determine the motion and drawing orientation.

### 13. What is event handling?
Pygame stores keyboard and window events in an event queue. The program processes those events each frame to handle pause, signal requests, day/night, speed, reset and quit.

### 14. What is the purpose of `pygame.display.flip()`?
It updates the display to show the newly drawn frame.

### 15. What is the difference between automatic and manual mode?
Automatic mode cycles through timed signal phases. In manual mode, the user requests horizontal or vertical green, while the controller still uses yellow and all-red intervals when changing direction.

### 16. What are the main limitations?
The model uses straight fixed lanes and simplified vehicle dynamics. It does not model turning vehicles, pedestrian behaviour, realistic acceleration/braking, traffic sensors or adaptive signal optimisation.

### 17. What enhancements could be added?
Pedestrian crossing phases, left/right turns, emergency vehicle priority, configurable traffic density, adaptive green timing, sound effects or saved simulation statistics.

### 18. Why are external images not required?
The project draws its objects using Pygame primitives. This keeps the project portable and makes the graphics operations easy to explain.

## Be ready to explain these functions

- `TrafficController.update()` — updates the current phase and timed transitions.
- `TrafficController.request_manual_green()` — handles safe manual direction changes.
- `TrafficSimulation.update()` — advances the simulation using elapsed time.
- `TrafficSimulation.update_lane()` — moves vehicles, enforces stop lines and following gaps.
- `draw_background()` — renders the environment and road markings.
- `draw_vehicle()` — draws a car using 2D primitives.
- `draw_dashboard()` — displays signal states, counters and controls.
- `main()` — implements the Pygame event, update and render loop.

## Viva demonstration order

1. Start the app and identify the main components.
2. Show automatic horizontal and vertical green phases.
3. Point out a vehicle stopping at the stop line and the queue spacing.
4. Use `H` and `V` to demonstrate safe manual phase changes.
5. Pause/resume and change day/night mode.
6. Explain translation, delta time, primitives and the state machine.
