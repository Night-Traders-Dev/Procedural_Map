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
