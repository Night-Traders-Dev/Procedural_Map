import random                                                             from rich.segment import Segment                                          from rich.style import Style                                              from textual.app import App, ComposeResult
from textual.strip import Strip                                           from textual.widget import Widget                                         from queue import PriorityQueue                                           import math                                                                                                                                                                                                                   class MapWidget(Widget):                                                      """Render a procedurally generated 2D RPG map."""                                                                                                   def __init__(self, width: int, height: int, num_villages: int) -> None:                                                                                 super().__init__()                                                        self.map_width = width                                                    self.map_height = height
        self.num_villages = num_villages                                          self.map_data = self.generate_map(width, height, num_villages)                                                                                  def generate_map(self, width: int, height: int, num_villages: int):           """Generate a random map with land, water, forest, villages, and roads."""                                                                          map_data = [["."] * width for _ in range(height)]                                                                                                   # Place water
        self.place_water(map_data)                                                                                                                          # Place forest                                                            self.place_forest(map_data)                                                                                                                         # Place villages                                                          villages = self.place_villages(width, height, num_villages, map_data)

        # Connect villages with roads
        self.connect_villages(villages, map_data)

        return map_data

    def place_water(self, map_data):
        """Place water on the map."""
        for y in range(self.map_height):
            for x in range(self.map_width):
                if random.random() < 0.2:  # 20% chance of water
                    map_data[y][x] = "~"  # Water

    def place_forest(self, map_data):
        """Place forest on the map."""
        for y in range(self.map_height):
            for x in range(self.map_width):
                if random.random() < 0.1:  # 10% chance of forest
                    map_data[y][x] = "T"  # Forest

    def place_villages(self, width: int, height: int, num_villages: int, map_data):
        """Place villages on the map."""
        villages = set()
        while len(villages) < num_villages:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            if map_data[y][x] == ".":
                villages.add((x, y))
        return villages

    def connect_villages(self, villages, map_data):
        """Connect villages with roads."""
        for v1 in villages:
            for v2 in villages:
                if v1 != v2:
                    path = self.find_shortest_path(v1, v2, map_data)
                    if path:
                        for x, y in path:
                            if map_data[y][x] != "V":  # Avoid overriding villages
                                map_data[y][x] = "#"

    def find_shortest_path(self, start, end, map_data):
        """Find the shortest path between two points using A* algorithm."""
        open_set = PriorityQueue()
        open_set.put((0, start))
        came_from = {}
        g_score = {start: 0}

        while not open_set.empty():
            current_cost, current = open_set.get()
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if 0 <= neighbor[0] < self.map_width and 0 <= neighbor[1] < self.map_height:
                    new_g_score = g_score[current] + 1
                    if neighbor not in g_score or new_g_score < g_score[neighbor]:
                        g_score[neighbor] = new_g_score
                        f_score = new_g_score + self.heuristic(neighbor, end)
                        open_set.put((f_score, neighbor))
                        came_from[neighbor] = current
        return None

    def heuristic(self, a, b):
        """Heuristic function (Euclidean distance) for A* algorithm."""
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget. y is relative to the top of the widget."""
        if y >= self.map_height:
            return Strip.blank(self.size.width)

        line = self.map_data[y]
        segments = [Segment(char, self.get_style(char)) for char in line]
        strip = Strip(segments, self.map_width)
        return strip

    def get_style(self, char: str) -> Style:
        """Return the style for a given map character."""
        if char == ".":
            return Style(color="green")  # Land
        elif char == "~":
            return Style(color="blue")  # Water
        elif char == "T":
            return Style(color="dark_green")  # Forest
        elif char == "#":
            return Style(color="yellow")  # Road
        elif char == "V":
            return Style(color="red")  # Village
        return Style()


class MapApp(App):
    """A simple app to show our map widget."""

    CSS_PATH = "map.tcss"  # Load the TCSS file

    def compose(self) -> ComposeResult:
        num_villages = 5
        return [MapWidget(40, 20, num_villages)]


if __name__ == "__main__":
    app = MapApp()
    app.run()