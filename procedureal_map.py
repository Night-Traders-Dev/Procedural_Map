import random
import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.containers import Vertical
from rich.text import Text


class MapWidget(Static):
    """Widget to represent the map."""

    def __init__(self, width, height, villager_groups, resources, weather_zones):
        super().__init__()
        self.width = width
        self.height = height
        self.villager_groups = villager_groups
        self.resources = resources
        self.weather_zones = weather_zones
        self.map = self.initialize_map()
        self.time_step = 0

    def initialize_map(self):
        """Initialize the map with empty tiles."""
        return [["░" for _ in range(self.width)] for _ in range(self.height)]

    def find_nearest_resource(self, villager):
        """Find the nearest resource to a villager."""
        nearest_resource = None
        nearest_distance = float("inf")
        for resource_type, resource_list in self.resources.items():
            for resource in resource_list:
                distance = self.calculate_distance(villager, resource)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_resource = resource
        return nearest_resource

    @staticmethod
    def calculate_distance(villager, resource):
        """Calculate Manhattan distance between a villager and a resource."""
        return abs(villager["x"] - resource["x"]) + abs(villager["y"] - resource["y"])

    async def update_villagers(self):
        """Update villagers based on resources and movement."""
        while True:
            groups_to_remove = []
            for group_id, group in list(self.villager_groups.items()):
                for villager in group["villagers"]:
                    nearest_resource = self.find_nearest_resource(villager)
                    if nearest_resource and self.calculate_distance(villager, nearest_resource) <= 2:
                        nearest_resource["quantity"] -= group["population"]
                        group["hunger"] += 5
                        group["thirst"] += 5
                        if nearest_resource["quantity"] <= 0:
                            self.resources[nearest_resource["type"]].remove(nearest_resource)
                    else:
                        dx = random.choice([-1, 0, 1])
                        dy = random.choice([-1, 0, 1])
                        villager["x"] = max(0, min(self.width - 1, villager["x"] + dx))
                        villager["y"] = max(0, min(self.height - 1, villager["y"] + dy))

                group["hunger"] -= 2
                group["thirst"] -= 2

                if group["hunger"] <= 0 or group["thirst"] <= 0:
                    groups_to_remove.append(group_id)

            for group_id in groups_to_remove:
                del self.villager_groups[group_id]

            await asyncio.sleep(0.5)  # Yield time to other tasks

    async def update_resources(self):
        """Grow resources over time based on weather and conditions."""
        while True:
            for resource_type, resource_list in self.resources.items():
                for resource in resource_list:
                    if resource_type == "~" and random.random() < 0.1:  # Water grows in rainy conditions
                        resource["quantity"] += random.randint(1, 3)
                    elif resource_type == "T" and random.random() < 0.05:  # Trees grow slower
                        resource["quantity"] += random.randint(1, 2)
            await asyncio.sleep(2)  # Resource update interval

    def refresh_map(self):
        """Update the map with current entities."""
        self.map = self.initialize_map()
        for resource_type, resource_list in self.resources.items():
            for resource in resource_list:
                self.map[resource["y"]][resource["x"]] = resource_type
        for group_id, group in self.villager_groups.items():
            for villager in group["villagers"]:
                self.map[villager["y"]][villager["x"]] = group["symbol"]

    def render(self) -> Text:
        """Render the map with colors."""
        result = Text()
        for row in self.map:
            for cell in row:
                if cell == "░":
                    result.append(cell, style="dim white")
                elif cell == "~":
                    result.append(cell, style="blue")
                elif cell == "T":
                    result.append(cell, style="green")
                elif cell in "RYGB":
                    result.append(
                        cell,
                        style="bold red" if cell == "R" else "bold yellow" if cell == "Y" else "bold green" if cell == "G" else "bold blue",
                    )
            result.append("\n")
        return result

    async def evolve(self):
        """Simulate map evolution."""
        while True:
            self.time_step += 1
            self.refresh_map()
            self.refresh()
            await asyncio.sleep(0.5)


class MetricsWidget(Static):
    """Widget for displaying simulation metrics."""

    def __init__(self, villager_groups, resources):
        super().__init__()
        self.villager_groups = villager_groups
        self.resources = resources
        self.start_time = asyncio.get_event_loop().time()

    async def update_metrics(self):
        """Update displayed metrics."""
        while True:
            elapsed_time = int(asyncio.get_event_loop().time() - self.start_time)
            total_population = sum(group["population"] for group in self.villager_groups.values())
            water_supply = sum(res["quantity"] for res in self.resources["~"])
            tree_supply = sum(res["quantity"] for res in self.resources["T"])
            metrics = f"Elapsed Time: {elapsed_time}s\n"
            metrics += f"Villager Groups: {len(self.villager_groups)}\n"
            metrics += f"Total Population: {total_population}\n"
            metrics += f"Water Supply: {water_supply}\n"
            metrics += f"Tree Supply: {tree_supply}\n"
            for group_id, group in self.villager_groups.items():
                metrics += f"Group {group_id} | Pop: {group['population']} Hunger: {group['hunger']} Thirst: {group['thirst']}\n"
            self.update(metrics)
            await asyncio.sleep(1)


class MapApp(App):
    """Main simulation app."""

    def __init__(self):
        super().__init__()
        self.villager_groups = {
            1: {"symbol": "R", "villagers": [{"x": random.randint(0, 39), "y": random.randint(0, 19)}], "population": 4, "hunger": 100, "thirst": 100},
            2: {"symbol": "Y", "villagers": [{"x": random.randint(0, 39), "y": random.randint(0, 19)}], "population": 4, "hunger": 100, "thirst": 100},
            3: {"symbol": "G", "villagers": [{"x": random.randint(0, 39), "y": random.randint(0, 19)}], "population": 4, "hunger": 100, "thirst": 100},
            4: {"symbol": "B", "villagers": [{"x": random.randint(0, 39), "y": random.randint(0, 19)}], "population": 4, "hunger": 100, "thirst": 100},
        }
        self.resources = {
            "~": [{"x": random.randint(0, 39), "y": random.randint(0, 19), "quantity": random.randint(10, 20)} for _ in range(5)],
            "T": [{"x": random.randint(0, 39), "y": random.randint(0, 19), "quantity": random.randint(5, 15)} for _ in range(5)],
        }

    def compose(self) -> ComposeResult:
        map_widget = MapWidget(40, 20, self.villager_groups, self.resources, [])
        metrics_widget = MetricsWidget(self.villager_groups, self.resources)
        asyncio.create_task(map_widget.evolve())
        asyncio.create_task(map_widget.update_villagers())
        asyncio.create_task(map_widget.update_resources())
        asyncio.create_task(metrics_widget.update_metrics())
        yield Vertical(map_widget, metrics_widget)


if __name__ == "__main__":
    app = MapApp()
    app.run()
