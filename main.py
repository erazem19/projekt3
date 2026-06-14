from __future__ import annotations

import argparse

from map_generator import END, FLOOR, START, WALL, generate_map, grid_to_ascii


CELL_SIZE = 14
PANEL_WIDTH = 280
COLORS = {
    WALL: (24, 28, 34),
    FLOOR: (210, 215, 220),
    START: (64, 180, 95),
    END: (214, 76, 76),
}
PATH_COLOR = (78, 143, 222)
ROOM_BORDER = (124, 143, 166)
TEXT = (235, 238, 242)
MUTED = (164, 174, 188)
PANEL = (38, 45, 54)
ACCENT = (106, 170, 255)


class InputBox:
    def __init__(self, label: str, value: int, minimum: int, maximum: int, x: int, y: int):
        self.label = label
        self.value = str(value)
        self.minimum = minimum
        self.maximum = maximum
        self.rect = None
        self.x = x
        self.y = y
        self.active = False

    def draw(self, pygame, screen, font, small_font):
        label_surface = small_font.render(f"{self.label} ({self.minimum}-{self.maximum})", True, MUTED)
        screen.blit(label_surface, (self.x, self.y))
        self.rect = pygame.Rect(self.x, self.y + 22, 210, 34)
        color = ACCENT if self.active else (86, 98, 116)
        pygame.draw.rect(screen, (25, 30, 37), self.rect, border_radius=4)
        pygame.draw.rect(screen, color, self.rect, width=2, border_radius=4)
        value_surface = font.render(self.value, True, TEXT)
        screen.blit(value_surface, (self.rect.x + 10, self.rect.y + 6))

    def handle_event(self, pygame, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_TAB):
                self.active = False
            elif event.unicode.isdigit() and len(self.value) < 5:
                self.value += event.unicode

    def number(self) -> int:
        raw = int(self.value or self.minimum)
        return max(self.minimum, min(self.maximum, raw))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BSP generator naključnih zemljevidov s preverjanjem BFS.")
    parser.add_argument("--width", type=int, default=80)
    parser.add_argument("--height", type=int, default=45)
    parser.add_argument("--rooms", type=int, default=18)
    parser.add_argument("--connectivity", type=int, default=25)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--ascii", action="store_true", help="Izpiše ustvarjen zemljevid in zapre program.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = generate_map(args.width, args.height, args.rooms, args.connectivity, args.seed)

    if args.ascii:
        print(f"Seed: {result.seed} | Poskusi: {result.attempts} | Dolžina poti: {len(result.path)}")
        print(grid_to_ascii(result.grid, result.path))
        return 0

    try:
        import pygame
    except ModuleNotFoundError:
        print("Pygame ni nameščen. Zaženi: python -m pip install -r requirements.txt")
        print("Zemljevid lahko vseeno prikažeš z ukazom: python main.py --ascii")
        return 1

    pygame.init()
    width_px = args.width * CELL_SIZE + PANEL_WIDTH
    height_px = args.height * CELL_SIZE
    screen = pygame.display.set_mode((width_px, height_px))
    pygame.display.set_caption("Generator naključnih zemljevidov")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)
    small_font = pygame.font.SysFont("consolas", 15)
    title_font = pygame.font.SysFont("consolas", 24, bold=True)

    boxes = [
        InputBox("Širina mreže", args.width, 25, 120, args.width * CELL_SIZE + 28, 88),
        InputBox("Višina mreže", args.height, 20, 70, args.width * CELL_SIZE + 28, 158),
        InputBox("Sobe", args.rooms, 2, 60, args.width * CELL_SIZE + 28, 228),
        InputBox("Povezanost %", args.connectivity, 0, 100, args.width * CELL_SIZE + 28, 298),
    ]
    show_path = True
    error = ""
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_g:
                    result, error = regenerate(boxes, result.seed + 1)
                    boxes = move_boxes(boxes, len(result.grid[0]) * CELL_SIZE + 28)
                    screen = pygame.display.set_mode((len(result.grid[0]) * CELL_SIZE + PANEL_WIDTH, len(result.grid) * CELL_SIZE))
                elif event.key == pygame.K_SPACE:
                    show_path = not show_path
            for box in boxes:
                box.handle_event(pygame, event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                button = pygame.Rect(len(result.grid[0]) * CELL_SIZE + 28, 380, 210, 38)
                if button.collidepoint(event.pos):
                    result, error = regenerate(boxes, result.seed + 1)
                    boxes = move_boxes(boxes, len(result.grid[0]) * CELL_SIZE + 28)
                    screen = pygame.display.set_mode((len(result.grid[0]) * CELL_SIZE + PANEL_WIDTH, len(result.grid) * CELL_SIZE))

        draw(pygame, screen, result, boxes, show_path, error, font, small_font, title_font)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return 0


def regenerate(boxes: list[InputBox], seed: int):
    try:
        result = generate_map(
            width=boxes[0].number(),
            height=boxes[1].number(),
            room_count=boxes[2].number(),
            connectivity=boxes[3].number(),
            seed=seed,
        )
        return result, ""
    except ValueError as exc:
        return generate_map(seed=seed), str(exc)
    except RuntimeError as exc:
        return generate_map(seed=seed), str(exc)


def move_boxes(boxes: list[InputBox], x: int) -> list[InputBox]:
    for box in boxes:
        box.x = x
    return boxes


def draw(pygame, screen, result, boxes, show_path, error, font, small_font, title_font):
    screen.fill((14, 17, 22))
    grid = result.grid
    path = set(result.path if show_path else [])

    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            color = PATH_COLOR if (x, y) in path and cell == FLOOR else COLORS[cell]
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    for room in result.rooms:
        pygame.draw.rect(
            screen,
            ROOM_BORDER,
            (room.x * CELL_SIZE, room.y * CELL_SIZE, room.w * CELL_SIZE, room.h * CELL_SIZE),
            width=1,
        )

    panel_x = len(grid[0]) * CELL_SIZE
    pygame.draw.rect(screen, PANEL, (panel_x, 0, PANEL_WIDTH, len(grid) * CELL_SIZE))
    screen.blit(title_font.render("Generator map", True, TEXT), (panel_x + 28, 24))
    screen.blit(small_font.render("BSP sobe + hodniki + BFS", True, MUTED), (panel_x + 28, 54))

    for box in boxes:
        box.draw(pygame, screen, font, small_font)

    button = pygame.Rect(panel_x + 28, 380, 210, 38)
    pygame.draw.rect(screen, ACCENT, button, border_radius=4)
    screen.blit(font.render("Ustvari (G)", True, (8, 17, 29)), (button.x + 34, button.y + 8))

    stats = [
        f"Seed: {result.seed}",
        f"Poskusi: {result.attempts}",
        f"Sobe: {len(result.rooms)}",
        f"Dolžina poti: {len(result.path)}",
        f"Pot: {'prikazana' if show_path else 'skrita'} (Space)",
    ]
    y = 442
    for stat in stats:
        screen.blit(small_font.render(stat, True, TEXT), (panel_x + 28, y))
        y += 24

    if error:
        screen.blit(small_font.render(error[:32], True, (255, 160, 120)), (panel_x + 28, y + 12))


if __name__ == "__main__":
    raise SystemExit(main())
