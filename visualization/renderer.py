import pygame
from typing import List, Dict
from models.core import Graph, Zone
from simulation.drone import DroneState


class Renderer:
    def __init__(self, graph: Graph) -> None:
        pygame.init()

        self.graph = graph

        self.width = 2400
        self.height = 1200
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Drone Simulation")

        self.clock = pygame.time.Clock()

        self.bg = pygame.image.load("assets/background.png").convert()

        self.drone_img = pygame.image.load(
            "assets/drone.png"
        ).convert_alpha()

        self.zone_img = pygame.image.load(
            "assets/normal.png"
        ).convert_alpha()

        self.blocked_img = pygame.image.load(
            "assets/blocked.png"
        ).convert_alpha()

        self.restricted_img = pygame.image.load(
            "assets/restricted.png"
        ).convert_alpha()

        self.priority_img = pygame.image.load(
            "assets/priority.png"
        ).convert_alpha()

        self.start_img = pygame.image.load(
            "assets/start.png"
        ).convert_alpha()

        self.end_img = pygame.image.load(
            "assets/blocked.png"
        ).convert_alpha()

        self._compute_layout()
        self._compute_sprite_size()

        self.bg = pygame.transform.smoothscale(
            self.bg,
            (self.width, self.height)
        )

        self.drone_img = self._scale_sprite(
            self.drone_img,
            self.drone_size
        )

        self.zone_img = self._scale_sprite(
            self.zone_img,
            self.zone_size
        )

        self.blocked_img = self._scale_sprite(
            self.blocked_img,
            self.zone_size
        )
        self.restricted_img = self._scale_sprite(
            self.restricted_img,
            self.zone_size
        )
        self.priority_img = self._scale_sprite(
            self.priority_img,
            self.zone_size
        )
        self.start_img = self._scale_sprite(
            self.start_img,
            self.zone_size
        )
        self.end_img = self._scale_sprite(
            self.end_img,
            self.zone_size
        )
        self.font = pygame.font.SysFont("Arial", 28)

    def _compute_layout(self) -> None:
        """Compute scaling and offsets to fit the graph"""
        xs = [zone.x for zone in self.graph.zones.values()]
        ys = [zone.y for zone in self.graph.zones.values()]

        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        graph_width = max_x - min_x
        graph_height = max_y - min_y

        if graph_width == 0:
            graph_width = 1
        if graph_height == 0:
            graph_height = 1

        nb_zones = len(self.graph.zones)

        if nb_zones <= 4:
            margin = 40
        elif nb_zones <= 8:
            margin = 70
        else:
            margin = 120

        usable_width = self.width - 2 * margin
        usable_height = self.height - 2 * margin

        is_horizontal = len(set(ys)) == 1
        is_vertical = len(set(xs)) == 1

        if is_horizontal:
            self.scale = usable_width / graph_width
        elif is_vertical:
            self.scale = usable_height / graph_height
        else:
            self.scale = min(
                usable_width / graph_width,
                usable_height / graph_height
            )

        self.scale = min(self.scale, 320)

        scaled_width = graph_width * self.scale
        scaled_height = graph_height * self.scale

        self.offset_x = (self.width - scaled_width) / 2
        self.offset_y = (self.height - scaled_height) / 2

        self.min_x = min_x
        self.min_y = min_y

    def _parse_color(self, color: str | None):
        if not color:
            return (200, 200, 200)

        COLORS = {
            "red": (220, 50, 50),
            "darkred": (139, 0, 0),
            "blue": (50, 120, 220),
            "green": (50, 200, 50),
            "purple": (160, 80, 200),
            "orange": (255, 140, 0),
            "yellow": (240, 220, 60),
            "gold": (255, 200, 0),
            "violet": (180, 80, 255),
            "black": (30, 30, 30),
            "white": (240, 240, 240),
            "brown": (139, 90, 43),
            "maroon": (128, 0, 0),
            "rainbow": (200, 200, 200)
        }
        return COLORS.get(color.strip().lower(), (200, 200, 200))

    def _compute_sprite_size(self) -> None:
        nb_zones = len(self.graph.zones)

        if nb_zones <= 4:
            self.zone_size = 240
            self.drone_size = 192
            return

        if nb_zones <= 8:
            self.zone_size = 180
            self.drone_size = 144
            return
        density_size = int(240 / max(nb_zones ** 0.5, 1))
        scale_size = int(self.scale * 0.18)
        base_size = max(24, min(max(density_size, scale_size), 42))
        self.zone_size = base_size
        self.drone_size = max(14, int(base_size * 0.8))

    def _scale_sprite(self, sprite, size: int):
        return pygame.transform.smoothscale(sprite, (size, size))

    def _to_screen(self, zone: Zone) -> tuple[int, int]:
        """Convert graph coordinates → screen coordinates"""
        x = self.offset_x + (zone.x - self.min_x) * self.scale
        y = self.offset_y + (zone.y - self.min_y) * self.scale
        return int(x), int(y)

    def _get_zone_sprite(self, zone: Zone):
        zone_type = zone.zone_type.strip().lower()
        if zone == self.graph.start:
            return self.start_img
        if zone == self.graph.end:
            return self.end_img
        if zone_type == "blocked":
            return self.blocked_img
        if zone_type == "restricted":
            return self.restricted_img
        if zone_type == "priority":
            return self.priority_img
        return self.zone_img

    def draw_turn_counter(self, turn: int) -> None:
        text = self.font.render(f"Turn: {turn}", True, (255, 255, 255))
        rect = text.get_rect()
        rect.bottomright = (self.width - 20, self.height - 20)
        self.screen.blit(text, rect)

    def draw_background(self) -> None:
        self.screen.blit(self.bg, (0, 0))

    def draw_connections(self) -> None:
        for conn in self.graph.connections:
            x1, y1 = self._to_screen(conn.zone1)
            x2, y2 = self._to_screen(conn.zone2)

            pygame.draw.line(
                self.screen,
                (180, 180, 180),
                (x1, y1),
                (x2, y2),
                2,
            )

    def draw_zones(self) -> None:
        for zone in self.graph.zones.values():
            x, y = self._to_screen(zone)

            color = self._parse_color(zone.color)
            radius = self.zone_size // 2
            pygame.draw.circle(
                self.screen,
                color,
                (x, y),
                radius
            )

            sprite = self._get_zone_sprite(zone)
            rect = sprite.get_rect(center=(x, y))

            self.screen.blit(sprite, rect)

    def draw_drones(
            self,
            drones: List[DroneState],
            positions_a: Dict[int, Zone],
            positions_b: Dict[int, Zone],
            alpha: float
    ) -> None:
        for drone in drones:
            zone_a = positions_a[drone.id]
            zone_b = positions_b[drone.id]

            x1, y1 = self._to_screen(zone_a)
            x2, y2 = self._to_screen(zone_b)

            x = x1 + (x2 - x1) * alpha
            y = y1 + (y2 - y1) * alpha

            rect = self.drone_img.get_rect(center=(int(x), int(y)))
            self.screen.blit(self.drone_img, rect)

    def run(self, history_positions, drones):

        running = True
        turn = 0
        frames_per_turn = 60
        frame = 0

        for i, positions in enumerate(history_positions):
            print(f"TURN {i}: {positions}")

        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw_background()
            self.draw_connections()
            self.draw_zones()

            logical_turn = min(turn, len(history_positions) - 1)
            self.draw_turn_counter(logical_turn)

            if turn < len(history_positions) - 1:

                positions = history_positions[turn]
                next_positions = history_positions[turn + 1]

                for drone in drones:

                    current_zone = positions[drone.id]
                    next_zone = next_positions[drone.id]

                    x1, y1 = self._to_screen(current_zone)
                    x2, y2 = self._to_screen(next_zone)

                    alpha = frame / frames_per_turn

                    x = x1 + (x2 - x1) * alpha
                    y = y1 + (y2 - y1) * alpha

                    rect = self.drone_img.get_rect(center=(int(x), int(y)))
                    self.screen.blit(self.drone_img, rect)

                frame += 1

                if frame >= frames_per_turn:
                    frame = 0
                    turn += 1
                    print("TURN AVANZA A:", turn)

            else:

                positions = history_positions[-1]

                for drone in drones:

                    current_zone = positions[drone.id]

                    x, y = self._to_screen(current_zone)

                    rect = self.drone_img.get_rect(center=(int(x), int(y)))
                    self.screen.blit(self.drone_img, rect)
            pygame.display.flip()
            self.clock.tick(80)

        pygame.quit()
