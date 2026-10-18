"""Smart Traffic Intersection Simulator — Computer Graphics project.

Built with Python and Pygame. All objects are rendered with 2D drawing primitives.

Controls
--------
SPACE : Pause / resume simulation
A     : Toggle automatic / manual traffic control
H     : Request horizontal traffic green (uses yellow + all-red clearance)
V     : Request vertical traffic green (uses yellow + all-red clearance)
N     : Toggle day / night scene
+ / - : Increase / decrease simulation speed
R     : Reset simulation
ESC   : Quit
"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass, field
from typing import Optional

import pygame

# -----------------------------------------------------------------------------
# Window and scene configuration
# -----------------------------------------------------------------------------
SCENE_W, PANEL_W, HEIGHT = 900, 320, 720
WIDTH = SCENE_W + PANEL_W
FPS = 60
TITLE = "Smart Traffic Intersection Simulator | Computer Graphics"

ROAD_LEFT, ROAD_RIGHT = 330, 500
ROAD_TOP, ROAD_BOTTOM = 260, 430
CAR_LENGTH, CAR_WIDTH = 56, 30
CAR_GAP = 22
STOP_GAP = 8

# The phase sequence includes an all-red clearance interval between directions.
AUTO_PHASES = [
    ("H_GREEN", 8.0),
    ("H_YELLOW", 2.0),
    ("ALL_RED", 1.0),
    ("V_GREEN", 8.0),
    ("V_YELLOW", 2.0),
    ("ALL_RED", 1.0),
]
PHASE_DURATION = {name: seconds for name, seconds in AUTO_PHASES}

# RGB palette
INK = (24, 32, 43)
WHITE = (245, 248, 250)
MUTED = (164, 178, 194)
ROAD = (55, 63, 73)
ROAD_EDGE = (139, 148, 157)
MARKING = (235, 236, 220)
GRASS_DAY = (111, 163, 93)
GRASS_NIGHT = (35, 63, 58)
SKY_DAY = (153, 211, 246)
SKY_NIGHT = (22, 32, 58)
SIGNAL_RED = (240, 64, 72)
SIGNAL_YELLOW = (255, 193, 57)
SIGNAL_GREEN = (59, 216, 129)
CAR_PALETTE = [
    (238, 91, 86), (64, 151, 224), (248, 190, 70),
    (137, 112, 205), (240, 241, 235), (71, 184, 145),
    (231, 127, 63), (106, 126, 147),
]


def clamp(value: float, low: float, high: float) -> float:
    """Clamp a value to an inclusive range."""
    return max(low, min(high, value))


@dataclass
class Vehicle:
    """A simple car represented by a position along its lane."""

    pos: float
    color: tuple[int, int, int]
    speed_factor: float = field(default_factory=lambda: random.uniform(0.90, 1.08))
    moving: bool = True


@dataclass
class Lane:
    """A single one-way lane that contains vehicles moving along one axis."""

    name: str
    axis: str                 # "x" for horizontal lanes; "y" for vertical lanes
    direction: int            # +1 means right/down; -1 means left/up
    lane_coord: int           # y for horizontal lanes, x for vertical lanes
    group: str                # "H" or "V", associated traffic signal group
    vehicles: list[Vehicle] = field(default_factory=list)
    spawn_timer: float = field(default_factory=lambda: random.uniform(0.7, 1.8))

    @property
    def axis_size(self) -> int:
        return SCENE_W if self.axis == "x" else HEIGHT

    @property
    def vehicle_length(self) -> int:
        return CAR_LENGTH

    def can_spawn(self) -> bool:
        """Avoid creating a new car too close to another car at the entry edge."""
        if not self.vehicles:
            return True
        if self.direction > 0:
            closest = min(vehicle.pos for vehicle in self.vehicles)
            return closest > CAR_LENGTH + CAR_GAP
        closest = max(vehicle.pos for vehicle in self.vehicles)
        return closest < self.axis_size - CAR_LENGTH - CAR_GAP

    def spawn(self) -> None:
        """Create a car just outside the entry edge of this lane."""
        if self.direction > 0:
            start = -CAR_LENGTH - 8
        else:
            start = self.axis_size + 8
        self.vehicles.append(Vehicle(start, random.choice(CAR_PALETTE)))
        self.spawn_timer = random.uniform(1.3, 2.7)

    def stop_position(self) -> float:
        """Return the car's top-left coordinate when stopped before the junction."""
        if self.axis == "x" and self.direction > 0:
            return ROAD_LEFT - CAR_LENGTH - STOP_GAP
        if self.axis == "x" and self.direction < 0:
            return ROAD_RIGHT + STOP_GAP
        if self.axis == "y" and self.direction > 0:
            return ROAD_TOP - CAR_LENGTH - STOP_GAP
        return ROAD_BOTTOM + STOP_GAP


class TrafficController:
    """Controls phases with safe yellow and all-red clearance transitions."""

    def __init__(self) -> None:
        self.auto_mode = True
        self.phase_index = 0
        self.phase = AUTO_PHASES[0][0]
        self.elapsed = 0.0
        self.pending_phase: Optional[str] = None
        self.transition_stage: Optional[str] = None
        self.transition_timer = 0.0

    def reset(self) -> None:
        self.__init__()

    def is_green(self, group: str) -> bool:
        return self.phase == ("H_GREEN" if group == "H" else "V_GREEN")

    def group_lamp(self, group: str) -> str:
        if group == "H":
            if self.phase == "H_GREEN":
                return "GREEN"
            if self.phase == "H_YELLOW":
                return "YELLOW"
        else:
            if self.phase == "V_GREEN":
                return "GREEN"
            if self.phase == "V_YELLOW":
                return "YELLOW"
        return "RED"

    def update(self, dt: float) -> None:
        if self.auto_mode:
            self.elapsed += dt
            # while handles occasional long frames without losing phase timing.
            while self.elapsed >= AUTO_PHASES[self.phase_index][1]:
                self.elapsed -= AUTO_PHASES[self.phase_index][1]
                self.phase_index = (self.phase_index + 1) % len(AUTO_PHASES)
                self.phase = AUTO_PHASES[self.phase_index][0]
            return

        if self.pending_phase is not None:
            self.transition_timer -= dt
            if self.transition_timer <= 0:
                if self.transition_stage == "yellow":
                    self.phase = "ALL_RED"
                    self.transition_stage = "red"
                    self.transition_timer = 0.9
                else:
                    self.phase = self.pending_phase
                    self.pending_phase = None
                    self.transition_stage = None
                    self.transition_timer = 0.0

    def request_manual_green(self, target: str) -> None:
        """Request H/V green; cross-direction changes pass through yellow + red."""
        self.auto_mode = False
        self.elapsed = 0.0
        self.pending_phase = None
        self.transition_stage = None
        self.transition_timer = 0.0

        if target == self.phase:
            return

        target_group = target[0]
        current_group = "H" if self.phase.startswith("H_") else (
            "V" if self.phase.startswith("V_") else None
        )

        if current_group == target_group:
            # Switching within one direction is safe because the other direction
            # remains red. This is mostly useful when cancelling a yellow phase.
            self.phase = target
            return

        if current_group is not None:
            self.phase = f"{current_group}_YELLOW"
            self.pending_phase = target
            self.transition_stage = "yellow"
            self.transition_timer = PHASE_DURATION[self.phase]
        else:
            self.phase = "ALL_RED"
            self.pending_phase = target
            self.transition_stage = "red"
            self.transition_timer = 0.9

    def toggle_auto(self) -> None:
        if self.auto_mode:
            self.auto_mode = False
            self.pending_phase = None
            self.transition_stage = None
            self.transition_timer = 0.0
            return

        # Resume automatic cycling from the current state. For duplicate all-red
        # entries, select the clearance phase that leads to the vertical green.
        if self.phase == "ALL_RED":
            self.phase_index = 2
        else:
            self.phase_index = next(
                (i for i, (phase, _) in enumerate(AUTO_PHASES) if phase == self.phase), 0
            )
        self.phase = AUTO_PHASES[self.phase_index][0]
        self.elapsed = 0.0
        self.auto_mode = True
        self.pending_phase = None
        self.transition_stage = None
        self.transition_timer = 0.0

    def time_remaining(self) -> Optional[float]:
        if self.auto_mode:
            return max(0.0, AUTO_PHASES[self.phase_index][1] - self.elapsed)
        if self.pending_phase is not None:
            return max(0.0, self.transition_timer)
        return None

    def display_phase(self) -> str:
        return self.phase.replace("_", " ")


class TrafficSimulation:
    def __init__(self) -> None:
        random.seed(17)
        self.controller = TrafficController()
        self.paused = False
        self.day_mode = True
        self.sim_speed = 1.0
        self.world_time = 0.0
        self.total_passed = 0
        self.lanes = self.create_lanes()
        self.seed_vehicles()

    @staticmethod
    def create_lanes() -> list[Lane]:
        return [
            Lane("H-E", "x", 1, 292, "H"),   # horizontal, moving right
            Lane("H-W", "x", -1, 368, "H"),  # horizontal, moving left
            Lane("V-S", "y", 1, 352, "V"),   # vertical, moving down
            Lane("V-N", "y", -1, 450, "V"),  # vertical, moving up
        ]

    def seed_vehicles(self) -> None:
        """Start with a few cars already visible so the scene is not empty."""
        initial = {
            "H-E": [40.0, 142.0],
            "H-W": [710.0],
            "V-S": [30.0, 110.0],
            "V-N": [545.0],
        }
        for lane in self.lanes:
            for position in initial[lane.name]:
                lane.vehicles.append(Vehicle(position, random.choice(CAR_PALETTE)))

    def reset(self) -> None:
        self.__init__()

    def update(self, real_dt: float) -> None:
        if self.paused:
            return
        dt = min(real_dt, 0.05) * self.sim_speed
        self.world_time += dt
        self.controller.update(dt)

        for lane in self.lanes:
            lane.spawn_timer -= dt
            if lane.spawn_timer <= 0:
                if lane.can_spawn():
                    lane.spawn()
                else:
                    lane.spawn_timer = 0.25
            self.update_lane(lane, dt)

    def update_lane(self, lane: Lane, dt: float) -> None:
        """Move vehicles front-to-back, respecting lights and safe following gaps."""
        # The leading vehicle is updated first so following cars use its new position.
        ordered = sorted(lane.vehicles, key=lambda car: car.pos, reverse=(lane.direction > 0))
        leader_pos: Optional[float] = None
        active: list[Vehicle] = []
        green = self.controller.is_green(lane.group)
        stop_pos = lane.stop_position()

        for car in ordered:
            old_pos = car.pos
            proposed = old_pos + lane.direction * 158.0 * car.speed_factor * dt

            # A car that has not crossed the stop line cannot enter on yellow/red.
            if not green:
                if lane.direction > 0 and old_pos <= stop_pos < proposed:
                    proposed = stop_pos
                elif lane.direction < 0 and old_pos >= stop_pos > proposed:
                    proposed = stop_pos

            # Keep a following distance from the already-updated vehicle ahead.
            if leader_pos is not None:
                if lane.direction > 0:
                    proposed = min(proposed, leader_pos - CAR_LENGTH - CAR_GAP)
                else:
                    proposed = max(proposed, leader_pos + CAR_LENGTH + CAR_GAP)

            car.pos = proposed
            car.moving = abs(car.pos - old_pos) > 0.05
            leader_pos = car.pos

            if lane.direction > 0 and car.pos > lane.axis_size + CAR_LENGTH:
                self.total_passed += 1
            elif lane.direction < 0 and car.pos + CAR_LENGTH < 0:
                self.total_passed += 1
            else:
                active.append(car)

        lane.vehicles = active

    def all_vehicles(self) -> list[Vehicle]:
        return [car for lane in self.lanes for car in lane.vehicles]

    def stopped_count(self) -> int:
        return sum(not car.moving for car in self.all_vehicles())


# -----------------------------------------------------------------------------
# Rendering helpers
# -----------------------------------------------------------------------------
def draw_text(surface: pygame.Surface, font: pygame.font.Font, text: str,
              color: tuple[int, int, int], x: int, y: int) -> None:
    surface.blit(font.render(text, True, color), (x, y))


def draw_cloud(surface: pygame.Surface, x: int, y: int) -> None:
    cloud = (237, 246, 252)
    pygame.draw.circle(surface, cloud, (x + 17, y + 12), 13)
    pygame.draw.circle(surface, cloud, (x + 34, y + 4), 17)
    pygame.draw.circle(surface, cloud, (x + 53, y + 13), 13)
    pygame.draw.rect(surface, cloud, (x + 15, y + 11, 40, 15), border_radius=7)


def draw_background(surface: pygame.Surface, sim: TrafficSimulation) -> None:
    sky = SKY_DAY if sim.day_mode else SKY_NIGHT
    grass = GRASS_DAY if sim.day_mode else GRASS_NIGHT
    surface.fill(sky, (0, 0, SCENE_W, HEIGHT))
    pygame.draw.rect(surface, grass, (0, 185, SCENE_W, HEIGHT - 185))

    if sim.day_mode:
        pygame.draw.circle(surface, (255, 222, 112), (76, 68), 29)
        cloud_bases = [(150, 64), (465, 112), (725, 54)]
        for base_x, base_y in cloud_bases:
            cloud_x = int((base_x + sim.world_time * 16) % (SCENE_W + 120) - 70)
            draw_cloud(surface, cloud_x, base_y)
    else:
        pygame.draw.circle(surface, (226, 233, 246), (76, 68), 23)
        # A small fixed star field.
        for sx, sy in [(180, 42), (270, 90), (395, 45), (565, 70), (665, 36), (820, 104), (745, 145)]:
            pygame.draw.circle(surface, (230, 236, 252), (sx, sy), 2)

    buildings = [
        (20, 112, 94, 96), (127, 82, 76, 126), (216, 130, 86, 78),
        (585, 100, 90, 108), (690, 68, 78, 140), (784, 122, 92, 86),
    ]
    day_building_colors = [(171, 184, 193), (194, 185, 170), (154, 174, 185),
                           (193, 198, 201), (164, 179, 194), (194, 184, 175)]
    night_building_colors = [(52, 65, 88), (60, 68, 91), (47, 64, 85),
                             (55, 70, 93), (45, 59, 83), (60, 67, 87)]
    palette = day_building_colors if sim.day_mode else night_building_colors
    for idx, (x, y, w, h) in enumerate(buildings):
        pygame.draw.rect(surface, palette[idx], (x, y, w, h), border_radius=3)
        pygame.draw.rect(surface, (95, 113, 130) if sim.day_mode else (34, 44, 64),
                         (x, y, w, h), 2, border_radius=3)
        for wx in range(x + 12, x + w - 8, 19):
            for wy in range(y + 12, y + h - 8, 23):
                if sim.day_mode:
                    window_color = (220, 235, 242)
                else:
                    window_color = (255, 207, 112) if (wx + wy + idx) % 3 else (83, 101, 128)
                pygame.draw.rect(surface, window_color, (wx, wy, 9, 12), border_radius=1)

    # Road network (the vertical road is drawn after the horizontal road).
    pygame.draw.rect(surface, ROAD, (0, ROAD_TOP, SCENE_W, ROAD_BOTTOM - ROAD_TOP))
    pygame.draw.rect(surface, ROAD, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))

    # Road edges and lane markings.
    pygame.draw.line(surface, ROAD_EDGE, (0, ROAD_TOP), (SCENE_W, ROAD_TOP), 3)
    pygame.draw.line(surface, ROAD_EDGE, (0, ROAD_BOTTOM), (SCENE_W, ROAD_BOTTOM), 3)
    pygame.draw.line(surface, ROAD_EDGE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 3)
    pygame.draw.line(surface, ROAD_EDGE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 3)

    for start in range(12, SCENE_W, 52):
        end = min(start + 27, SCENE_W)
        if end < ROAD_LEFT - 1 or start > ROAD_RIGHT + 1:
            pygame.draw.line(surface, MARKING, (start, 345), (end, 345), 3)
    for start in range(8, HEIGHT, 52):
        end = min(start + 27, HEIGHT)
        if end < ROAD_TOP - 1 or start > ROAD_BOTTOM + 1:
            pygame.draw.line(surface, MARKING, (415, start), (415, end), 3)

    # Stop lines mark the four approaches.
    pygame.draw.line(surface, WHITE, (ROAD_LEFT - STOP_GAP, 279), (ROAD_LEFT - STOP_GAP, 330), 5)
    pygame.draw.line(surface, WHITE, (ROAD_RIGHT + STOP_GAP, 356), (ROAD_RIGHT + STOP_GAP, 411), 5)
    pygame.draw.line(surface, WHITE, (340, ROAD_TOP - STOP_GAP), (402, ROAD_TOP - STOP_GAP), 5)
    pygame.draw.line(surface, WHITE, (427, ROAD_BOTTOM + STOP_GAP), (490, ROAD_BOTTOM + STOP_GAP), 5)



def active_lamp_color(group: str, lamp: str, controller: TrafficController) -> tuple[int, int, int]:
    active = controller.group_lamp(group)
    base = {"RED": SIGNAL_RED, "YELLOW": SIGNAL_YELLOW, "GREEN": SIGNAL_GREEN}
    color = base[lamp]
    if active == lamp:
        return color
    return tuple(max(20, int(channel * 0.24)) for channel in color)


def draw_signal_head(surface: pygame.Surface, x: int, y: int, group: str,
                     controller: TrafficController) -> None:
    """Draw a physical-looking three-lamp signal using circles and rectangles."""
    pygame.draw.line(surface, (80, 91, 99), (x + 18, y + 76), (x + 18, y + 105), 5)
    pygame.draw.rect(surface, (29, 34, 42), (x, y, 36, 82), border_radius=8)
    pygame.draw.rect(surface, (87, 94, 103), (x, y, 36, 82), 2, border_radius=8)
    lamps = [("RED", SIGNAL_RED), ("YELLOW", SIGNAL_YELLOW), ("GREEN", SIGNAL_GREEN)]
    for i, (name, _color) in enumerate(lamps):
        pygame.draw.circle(surface, active_lamp_color(group, name, controller), (x + 18, y + 15 + i * 26), 8)


def draw_vehicle(surface: pygame.Surface, lane: Lane, car: Vehicle) -> None:
    """Draw an oriented car from basic rectangles, circles and polygons."""
    body = car.color
    shadow = (20, 25, 31)
    glass = (183, 220, 234)
    if lane.axis == "x":
        x, y = int(car.pos), lane.lane_coord
        body_rect = pygame.Rect(x, y, CAR_LENGTH, CAR_WIDTH)
        pygame.draw.rect(surface, shadow, body_rect.move(0, 3), border_radius=7)
        pygame.draw.rect(surface, body, body_rect, border_radius=7)
        pygame.draw.rect(surface, glass, (x + 13, y + 4, 27, 10), border_radius=3)
        pygame.draw.line(surface, (40, 48, 58), (x + 27, y + 4), (x + 27, y + 14), 2)
        pygame.draw.circle(surface, (25, 29, 34), (x + 13, y + CAR_WIDTH - 1), 6)
        pygame.draw.circle(surface, (25, 29, 34), (x + CAR_LENGTH - 13, y + CAR_WIDTH - 1), 6)
        front_x = x + CAR_LENGTH - 3 if lane.direction > 0 else x + 1
        lamp_color = (255, 236, 164) if lane.direction > 0 else (255, 88, 88)
        pygame.draw.rect(surface, lamp_color, (front_x, y + 7, 3, 5), border_radius=1)
    else:
        x, y = lane.lane_coord, int(car.pos)
        body_rect = pygame.Rect(x, y, CAR_WIDTH, CAR_LENGTH)
        pygame.draw.rect(surface, shadow, body_rect.move(3, 0), border_radius=7)
        pygame.draw.rect(surface, body, body_rect, border_radius=7)
        pygame.draw.rect(surface, glass, (x + 4, y + 14, 22, 28), border_radius=3)
        pygame.draw.line(surface, (40, 48, 58), (x + 4, y + 28), (x + 26, y + 28), 2)
        for wy in (y + 13, y + CAR_LENGTH - 13):
            pygame.draw.circle(surface, (25, 29, 34), (x + 1, wy), 5)
            pygame.draw.circle(surface, (25, 29, 34), (x + CAR_WIDTH - 1, wy), 5)
        front_y = y + CAR_LENGTH - 3 if lane.direction > 0 else y + 1
        lamp_color = (255, 236, 164) if lane.direction > 0 else (255, 88, 88)
        pygame.draw.rect(surface, lamp_color, (x + 7, front_y, 5, 3), border_radius=1)


def draw_world_signals(surface: pygame.Surface, controller: TrafficController) -> None:
    # Horizontal-traffic light by the west approach; vertical by the north approach.
    draw_signal_head(surface, 258, 168, "H", controller)
    draw_signal_head(surface, 526, 142, "V", controller)


def draw_stat_card(surface: pygame.Surface, x: int, y: int, w: int, h: int,
                   title: str, value: str, font: pygame.font.Font,
                   small_font: pygame.font.Font, accent: tuple[int, int, int]) -> None:
    pygame.draw.rect(surface, (35, 47, 63), (x, y, w, h), border_radius=12)
    pygame.draw.rect(surface, (57, 71, 89), (x, y, w, h), 1, border_radius=12)
    pygame.draw.rect(surface, accent, (x, y + 12, 4, h - 24), border_radius=2)
    draw_text(surface, small_font, title.upper(), MUTED, x + 16, y + 10)
    draw_text(surface, font, value, WHITE, x + 16, y + 32)


def draw_dashboard(surface: pygame.Surface, sim: TrafficSimulation,
                   title_font: pygame.font.Font, font: pygame.font.Font,
                   small_font: pygame.font.Font) -> None:
    x0 = SCENE_W
    pygame.draw.rect(surface, (22, 30, 43), (x0, 0, PANEL_W, HEIGHT))
    pygame.draw.line(surface, (55, 68, 86), (x0, 0), (x0, HEIGHT), 2)
    left = x0 + 22

    draw_text(surface, title_font, "SMART TRAFFIC", WHITE, left, 22)
    draw_text(surface, title_font, "INTERSECTION", WHITE, left, 56)
    draw_text(surface, small_font, "2D COMPUTER GRAPHICS SIMULATION", MUTED, left, 96)

    # Current signal phase and timer.
    pygame.draw.rect(surface, (35, 47, 63), (left, 128, 276, 112), border_radius=13)
    draw_text(surface, small_font, "TRAFFIC CONTROLLER", MUTED, left + 15, 141)
    phase_color = {
        "H_GREEN": SIGNAL_GREEN, "V_GREEN": SIGNAL_GREEN,
        "H_YELLOW": SIGNAL_YELLOW, "V_YELLOW": SIGNAL_YELLOW,
        "ALL_RED": SIGNAL_RED,
    }.get(sim.controller.phase, WHITE)
    draw_text(surface, font, sim.controller.display_phase(), phase_color, left + 15, 166)
    mode = "AUTOMATIC" if sim.controller.auto_mode else "MANUAL"
    draw_text(surface, small_font, f"MODE: {mode}", WHITE, left + 15, 203)
    remaining = sim.controller.time_remaining()
    if remaining is not None:
        timer_label = f"{remaining:0.1f}s"
        draw_text(surface, font, timer_label, WHITE, left + 204, 198)

    active = len(sim.all_vehicles())
    stopped = sim.stopped_count()
    draw_stat_card(surface, left, 254, 130, 82, "Cars active", str(active), font, small_font, (64, 164, 224))
    draw_stat_card(surface, left + 144, 254, 132, 82, "Passed", str(sim.total_passed), font, small_font, SIGNAL_GREEN)
    draw_stat_card(surface, left, 348, 130, 82, "Stopped", str(stopped), font, small_font, SIGNAL_YELLOW)
    draw_stat_card(surface, left + 144, 348, 132, 82, "Speed", f"{sim.sim_speed:.1f}x", font, small_font, (181, 143, 226))

    # Mini signal status summary.
    draw_text(surface, font, "SIGNAL STATUS", WHITE, left, 451)
    for row, group, label in [(0, "H", "HORIZONTAL"), (1, "V", "VERTICAL")]:
        y = 486 + row * 42
        lamp = sim.controller.group_lamp(group)
        lamp_color = {"RED": SIGNAL_RED, "YELLOW": SIGNAL_YELLOW, "GREEN": SIGNAL_GREEN}[lamp]
        pygame.draw.rect(surface, (35, 47, 63), (left, y, 276, 32), border_radius=8)
        pygame.draw.circle(surface, lamp_color, (left + 17, y + 16), 6)
        draw_text(surface, small_font, label, WHITE, left + 32, y + 8)
        draw_text(surface, small_font, lamp, lamp_color, left + 205, y + 8)

    draw_text(surface, font, "CONTROLS", WHITE, left, 585)
    controls = [
        "SPACE  Pause / resume",
        "A         Automatic / manual",
        "H / V   Request a green phase",
        "N         Day / night",
        "+ / -    Simulation speed",
        "R         Reset     ESC  Quit",
    ]
    for i, line in enumerate(controls):
        draw_text(surface, small_font, line, MUTED, left, 614 + i * 17)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont("arial", 24, bold=True)
    font = pygame.font.SysFont("arial", 18, bold=True)
    small_font = pygame.font.SysFont("arial", 13)
    large_font = pygame.font.SysFont("arial", 26, bold=True)
    sim = TrafficSimulation()
    running = True

    while running:
        real_dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    sim.paused = not sim.paused
                elif event.key == pygame.K_a:
                    sim.controller.toggle_auto()
                elif event.key == pygame.K_h:
                    sim.controller.request_manual_green("H_GREEN")
                elif event.key == pygame.K_v:
                    sim.controller.request_manual_green("V_GREEN")
                elif event.key == pygame.K_n:
                    sim.day_mode = not sim.day_mode
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    sim.sim_speed = clamp(sim.sim_speed + 0.25, 0.5, 2.5)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    sim.sim_speed = clamp(sim.sim_speed - 0.25, 0.5, 2.5)
                elif event.key == pygame.K_r:
                    sim.reset()

        sim.update(real_dt)
        draw_background(screen, sim)
        for lane in sim.lanes:
            for car in lane.vehicles:
                draw_vehicle(screen, lane, car)
        draw_world_signals(screen, sim.controller)
        draw_dashboard(screen, sim, title_font, large_font, small_font)

        if sim.paused:
            overlay = pygame.Surface((SCENE_W, HEIGHT), pygame.SRCALPHA)
            overlay.fill((12, 18, 28, 130))
            screen.blit(overlay, (0, 0))
            message = title_font.render("SIMULATION PAUSED", True, WHITE)
            screen.blit(message, message.get_rect(center=(SCENE_W // 2, HEIGHT // 2)))

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
