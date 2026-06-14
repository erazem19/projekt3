from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import random
from typing import Iterable


WALL = 0
FLOOR = 1
START = 2
END = 3


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def right(self) -> int:
        return self.x + self.w - 1

    @property
    def bottom(self) -> int:
        return self.y + self.h - 1

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)

    def shrink_randomly(self, rng: random.Random, min_room_size: int) -> "Rect":
        max_w = max(min_room_size, self.w - 2)
        max_h = max(min_room_size, self.h - 2)
        room_w = rng.randint(min_room_size, max_w)
        room_h = rng.randint(min_room_size, max_h)
        room_x = rng.randint(self.x + 1, self.x + self.w - room_w - 1)
        room_y = rng.randint(self.y + 1, self.y + self.h - room_h - 1)
        return Rect(room_x, room_y, room_w, room_h)


@dataclass
class MapResult:
    grid: list[list[int]]
    rooms: list[Rect]
    start: tuple[int, int]
    end: tuple[int, int]
    path: list[tuple[int, int]]
    attempts: int
    seed: int


def generate_map(
    width: int = 80,
    height: int = 45,
    room_count: int = 18,
    connectivity: int = 25,
    seed: int | None = None,
    min_room_size: int = 4,
    max_attempts: int = 40,
) -> MapResult:
    """Ustvari in preveri mrežni zemljevid v slogu ječe.

    Algoritem z BSP razdeli prostor na regije za sobe, nato središča sob
    poveže z minimalnim vpetim drevesom in dodatnimi povezavami. BFS preveri,
    da so vse sobe in izbrana pot med začetkom ter koncem dosegljive.
    """
    if width < 25 or height < 20:
        raise ValueError("Grid must be at least 25 x 20.")
    if room_count < 2:
        raise ValueError("At least 2 rooms are required.")
    if not 0 <= connectivity <= 100:
        raise ValueError("Connectivity must be between 0 and 100.")

    base_seed = seed if seed is not None else random.randrange(1_000_000_000)
    for attempt in range(1, max_attempts + 1):
        rng = random.Random(base_seed + attempt - 1)
        grid = [[WALL for _ in range(width)] for _ in range(height)]
        leaves = _split_bsp(Rect(1, 1, width - 2, height - 2), room_count, min_room_size, rng)
        rooms = [leaf.shrink_randomly(rng, min_room_size) for leaf in leaves]

        for room in rooms:
            _carve_room(grid, room)

        edges = _choose_connections(rooms, connectivity, rng)
        for a, b in edges:
            _carve_winding_corridor(grid, rooms[a].center, rooms[b].center, rng)

        start, end = _farthest_room_pair(rooms)
        path = bfs_path(grid, start, end)
        if path and _all_room_centers_reachable(grid, rooms, start):
            grid[start[1]][start[0]] = START
            grid[end[1]][end[0]] = END
            return MapResult(grid, rooms, start, end, path, attempt, base_seed)

    raise RuntimeError("Could not generate a fully connected map. Try fewer rooms or a larger grid.")


def bfs_path(
    grid: list[list[int]],
    start: tuple[int, int],
    end: tuple[int, int],
) -> list[tuple[int, int]]:
    queue: deque[tuple[int, int]] = deque([start])
    previous: dict[tuple[int, int], tuple[int, int] | None] = {start: None}

    while queue:
        current = queue.popleft()
        if current == end:
            break

        for neighbor in _walkable_neighbors(grid, current):
            if neighbor not in previous:
                previous[neighbor] = current
                queue.append(neighbor)

    if end not in previous:
        return []

    path = []
    current: tuple[int, int] | None = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    return path


def grid_to_ascii(grid: list[list[int]], path: Iterable[tuple[int, int]] = ()) -> str:
    path_cells = set(path)
    chars = {
        WALL: "#",
        FLOOR: ".",
        START: "S",
        END: "E",
    }
    lines = []
    for y, row in enumerate(grid):
        line = []
        for x, cell in enumerate(row):
            line.append("*" if (x, y) in path_cells and cell == FLOOR else chars[cell])
        lines.append("".join(line))
    return "\n".join(lines)


def _split_bsp(rect: Rect, target_count: int, min_room_size: int, rng: random.Random) -> list[Rect]:
    leaves = [rect]
    min_leaf_size = min_room_size * 2 + 3

    while len(leaves) < target_count:
        candidates = [leaf for leaf in leaves if leaf.w >= min_leaf_size * 2 or leaf.h >= min_leaf_size * 2]
        if not candidates:
            break

        leaf = max(candidates, key=lambda item: item.w * item.h)
        leaves.remove(leaf)
        left, right = _split_leaf(leaf, min_leaf_size, rng)
        leaves.extend([left, right])

    return leaves[:target_count]


def _split_leaf(rect: Rect, min_leaf_size: int, rng: random.Random) -> tuple[Rect, Rect]:
    split_vertical = rect.w > rect.h
    if rect.w / max(1, rect.h) < 0.75:
        split_vertical = False
    elif rect.h / max(1, rect.w) < 0.75:
        split_vertical = True
    elif rect.w >= min_leaf_size * 2 and rect.h >= min_leaf_size * 2:
        split_vertical = rng.choice([True, False])

    if split_vertical:
        split = rng.randint(min_leaf_size, rect.w - min_leaf_size)
        return Rect(rect.x, rect.y, split, rect.h), Rect(rect.x + split, rect.y, rect.w - split, rect.h)

    split = rng.randint(min_leaf_size, rect.h - min_leaf_size)
    return Rect(rect.x, rect.y, rect.w, split), Rect(rect.x, rect.y + split, rect.w, rect.h - split)


def _carve_room(grid: list[list[int]], room: Rect) -> None:
    for y in range(room.y, room.y + room.h):
        for x in range(room.x, room.x + room.w):
            grid[y][x] = FLOOR


def _choose_connections(rooms: list[Rect], connectivity: int, rng: random.Random) -> list[tuple[int, int]]:
    all_edges = []
    for i, room_a in enumerate(rooms):
        ax, ay = room_a.center
        for j in range(i + 1, len(rooms)):
            bx, by = rooms[j].center
            distance = abs(ax - bx) + abs(ay - by)
            all_edges.append((distance, i, j))
    all_edges.sort()

    parent = list(range(len(rooms)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    mst: list[tuple[int, int]] = []
    extras: list[tuple[int, int]] = []
    for _, a, b in all_edges:
        root_a, root_b = find(a), find(b)
        if root_a != root_b:
            parent[root_b] = root_a
            mst.append((a, b))
        else:
            extras.append((a, b))

    rng.shuffle(extras)
    extra_count = round(len(extras) * (connectivity / 100))
    return mst + extras[:extra_count]


def _carve_winding_corridor(
    grid: list[list[int]],
    start: tuple[int, int],
    end: tuple[int, int],
    rng: random.Random,
) -> None:
    x, y = start
    end_x, end_y = end
    grid[y][x] = FLOOR

    while (x, y) != (end_x, end_y):
        horizontal_first = rng.random() < 0.55
        if horizontal_first and x != end_x:
            x += 1 if end_x > x else -1
        elif y != end_y:
            y += 1 if end_y > y else -1
        elif x != end_x:
            x += 1 if end_x > x else -1

        _carve_corridor_cell(grid, x, y)


def _carve_corridor_cell(grid: list[list[int]], x: int, y: int) -> None:
    height = len(grid)
    width = len(grid[0])
    for yy in range(max(1, y - 1), min(height - 1, y + 2)):
        for xx in range(max(1, x - 1), min(width - 1, x + 2)):
            if abs(xx - x) + abs(yy - y) <= 1:
                grid[yy][xx] = FLOOR


def _farthest_room_pair(rooms: list[Rect]) -> tuple[tuple[int, int], tuple[int, int]]:
    best_distance = -1
    best_pair = (rooms[0].center, rooms[-1].center)
    for i, room_a in enumerate(rooms):
        ax, ay = room_a.center
        for room_b in rooms[i + 1 :]:
            bx, by = room_b.center
            distance = abs(ax - bx) + abs(ay - by)
            if distance > best_distance:
                best_distance = distance
                best_pair = (room_a.center, room_b.center)
    return best_pair


def _all_room_centers_reachable(grid: list[list[int]], rooms: list[Rect], start: tuple[int, int]) -> bool:
    seen = {start}
    queue: deque[tuple[int, int]] = deque([start])
    while queue:
        current = queue.popleft()
        for neighbor in _walkable_neighbors(grid, current):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)

    return all(room.center in seen for room in rooms)


def _walkable_neighbors(grid: list[list[int]], point: tuple[int, int]) -> Iterable[tuple[int, int]]:
    x, y = point
    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
        if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] != WALL:
            yield (nx, ny)
