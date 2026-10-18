# Test Cases

Run each test visually after launching `traffic_intersection.py`.

| ID | Test | Steps | Expected result |
|---|---|---|---|
| T1 | Startup | Launch the script | Window opens with intersection, signal heads, vehicles and dashboard |
| T2 | Automatic phase cycle | Wait through one full cycle | Horizontal and vertical groups alternate green; yellow and all-red clearance phases appear |
| T3 | Red-light stop | Observe a car approaching a red signal | Car stops before its approach stop line |
| T4 | Green-light movement | Wait until the car's group is green | Waiting car advances through the intersection |
| T5 | Queue spacing | Allow multiple cars to queue at one light | Cars remain separated and do not overlap in a lane |
| T6 | Manual phase request | Press `H`, then `V` | Phase transition uses yellow and all-red clearance when switching directions |
| T7 | Pause/resume | Press `SPACE` twice | Vehicles and phase timer freeze, then resume |
| T8 | Day/night | Press `N` | Background, buildings and windows change appearance |
| T9 | Speed control | Press `+` and `-` | Simulation timing and vehicle movement speed change |
| T10 | Reset | Press `R` | Vehicles, controller and counters reset |
| T11 | Quit | Press `ESC` | Window closes cleanly |

Note observations and include screenshots for T2, T3, T4, T6 and T8 in the report.
