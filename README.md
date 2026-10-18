# Smart Traffic Intersection Simulator

A slightly advanced 2D Computer Graphics mini-project built with **Python 3 and Pygame**. The scene is drawn using Pygame's drawing primitives; no external image or audio assets are needed.

## Features

- Four one-way lanes through a crossroad (two horizontal, two vertical).
- Automatic signal phases: horizontal green → horizontal yellow → all-red clearance → vertical green → vertical yellow → all-red clearance.
- Cars obey stop lines on red/yellow and resume on green.
- Vehicles maintain a following gap to avoid overlapping in a lane.
- Manual horizontal/vertical green requests with yellow and all-red clearance when switching directions.
- Animated clouds, day/night mode, speed control and pause/resume.
- Live panel showing current phase, signal state, active/stopped vehicles and total vehicles that passed.
- Keyboard controls and reset option.

## Requirements

- Python 3.10 or newer recommended.
- Pygame 2.5 or newer.
- Windows, macOS, or Linux with a desktop/display session.

## Setup

1. Extract the ZIP and open this folder in VS Code.
2. Open a terminal in this folder.
3. (Recommended) Create and activate a virtual environment:

   **Windows PowerShell**
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Launch the project:

   **Windows**
   ```powershell
   py traffic_intersection.py
   ```

   **macOS/Linux**
   ```bash
   python3 traffic_intersection.py
   ```

If `py` is not available on Windows, use `python` instead. If installation fails, check that Python is installed and the internet connection is available.

## Controls

| Key | Action |
|---|---|
| `SPACE` | Pause / resume |
| `A` | Toggle automatic / manual control |
| `H` | Request horizontal traffic green |
| `V` | Request vertical traffic green |
| `N` | Toggle day / night scene |
| `+` / `-` | Increase / decrease simulation speed |
| `R` | Reset simulation |
| `ESC` | Quit |

Manual H/V changes use yellow and all-red clearance before giving green to the other direction. Use the dashboard to see the current phase.

## Concepts demonstrated

1. **2D primitives:** rectangles, circles, lines and polygons-like composed shapes.
2. **Translation:** the position of each vehicle changes over time.
3. **Frame-based animation:** the scene is redrawn continuously.
4. **Time-based motion:** movement uses elapsed frame time (`dt`) and speed, rather than a fixed number of pixels per frame.
5. **Conditional logic:** a lane's signal phase determines whether a vehicle can cross its stop line.
6. **Basic collision avoidance:** vehicles maintain minimum following distance within each lane.
7. **Event handling:** `pygame.event.get()` processes keyboard and window events.
8. **State machine:** the traffic controller moves between green, yellow and all-red phases.

## Algorithm

1. Initialize Pygame, the display, fonts, clock, controller, lanes and initial vehicles.
2. At each frame, process keyboard events.
3. Calculate elapsed time and update the traffic controller.
4. For each lane, spawn a vehicle when its entry zone is clear.
5. Update vehicles front-to-back; stop at the stop line unless the lane has green, and preserve following gaps.
6. Remove vehicles that leave the scene and increment the passed-vehicle counter.
7. Draw the background, roads, cars, signal heads and dashboard.
8. Refresh the display and repeat until the user quits.

## Suggested 3–7 day plan

### Day 1 — Environment and static scene
- Install Python and Pygame.
- Draw the background, road cross, lane markings and stop lines.
- Explain the choice of primitives in your report.

### Day 2 — Vehicle objects and translation
- Create the `Vehicle` and `Lane` data structures.
- Draw horizontal and vertical vehicles.
- Implement time-based movement.

### Day 3 — Signal state machine
- Implement green, yellow, and all-red phases.
- Add stop-line rules for each approach.
- Test red/yellow stopping and green movement.

### Day 4 — Queues and interaction
- Add vehicle spawn timing, following gaps, keyboard controls and reset.
- Fix spacing and signal transitions.

### Day 5 — Dashboard and visual polish
- Add the status panel, statistics, moving clouds and day/night mode.
- Capture screenshots for documentation.

### Day 6 — Testing and report
- Execute all test cases in `TEST_CASES.md`.
- Prepare the problem statement, algorithm, flowchart, results and limitations.

### Day 7 — Viva rehearsal
- Explain the main loop, translation, delta time, state machine and stop-line logic without reading from the code.

With a 3-day deadline, prioritise Days 1–4, then verify the controls and practise the viva.

## Test checklist

See [`TEST_CASES.md`](TEST_CASES.md) for expected behaviours.

## Recommended report structure

1. Title page
2. Abstract
3. Problem statement and objectives
4. Hardware/software requirements
5. Computer Graphics concepts used
6. System design and phase-state diagram
7. Algorithm and flowchart
8. Implementation and important code snippets
9. Results with screenshots of horizontal green, vertical green, yellow and day/night mode
10. Test cases
11. Limitations and future enhancements
12. Conclusion
13. References

## Limitations and future work

This is an educational 2D model, not a real traffic-control system. Cars travel straight in fixed lanes; pedestrian crossings, turning paths, sensor-based adaptive control and physical traffic dynamics are not modelled. Extensions could include pedestrian signals, emergency vehicles, turn lanes, adaptive green duration or a user-configurable traffic density.

## Official reference

- Pygame documentation: https://www.pygame.org/docs/
