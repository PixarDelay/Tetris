import curses
import random
import time


COLUMNS = 10
ROWS = 22  
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1], [1, 1]],  # O
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]]   # J
]

COLORS = [1, 2, 3, 4, 5, 6, 7]

class Tetris:
    def __init__(self, stdscr, language='en'):
        self.stdscr = stdscr
        self.grid = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.level = 1
        self.game_over = False
        self.language = language
        self.stdscr.nodelay(1)
        self.stdscr.timeout(500)

        curses.start_color()
        for i in range(1, 8):
            curses.init_pair(i, i, 0)

    def new_piece(self):
        shape = random.choice(SHAPES)
        color = random.choice(COLORS)
        return {"shape": shape, "color": color, "x": COLUMNS // 2 - len(shape[0]) // 2, "y": 0}

    def draw_grid(self):
        for y in range(ROWS):
            for x in range(COLUMNS):
                if self.grid[y][x]:
                    self.stdscr.addch(y, x, '#', curses.color_pair(self.grid[y][x]))
                else:
                    self.stdscr.addch(y, x, ' ')

    def draw_piece(self, piece):
        shape = piece["shape"]
        color = piece["color"]
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    self.stdscr.addch(piece["y"] + y, piece["x"] + x, '#', curses.color_pair(color))

    def valid_space(self, piece, offset_x=0, offset_y=0):
        shape = piece["shape"]
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece["x"] + x + offset_x
                    new_y = piece["y"] + y + offset_y
                    if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS:
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        return True

    def freeze_piece(self):
        shape = self.current_piece["shape"]
        color = self.current_piece["color"]
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece["y"] + y][self.current_piece["x"] + x] = color
        self.clear_lines()

    def clear_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(row)]
        for i in lines_to_clear:
            self.grid.pop(i)
            self.grid.insert(0, [0 for _ in range(COLUMNS)])
            self.score += 100
        if lines_to_clear:
            self.level = self.score // 500 + 1
            self.stdscr.timeout(max(100, 500 - (self.level - 1) * 50))

    def move_piece(self, dx, dy):
        if self.valid_space(self.current_piece, dx, dy):
            self.current_piece["x"] += dx
            self.current_piece["y"] += dy
        elif dy > 0:
            self.freeze_piece()
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
            if not self.valid_space(self.current_piece):
                self.game_over = True

    def rotate_piece(self):
        shape = self.current_piece["shape"]
        rotated_shape = list(zip(*shape[::-1]))
        original_shape = self.current_piece["shape"]
        self.current_piece["shape"] = rotated_shape
        if not self.valid_space(self.current_piece):
            self.current_piece["shape"] = original_shape

    def draw_info(self):
        if self.language == 'en':
            self.stdscr.addstr(0, COLUMNS + 2, f"Score: {self.score}")
            self.stdscr.addstr(1, COLUMNS + 2, f"Level: {self.level}")
            self.stdscr.addstr(3, COLUMNS + 2, "Controls:")
            self.stdscr.addstr(4, COLUMNS + 2, "W - Rotate")
            self.stdscr.addstr(5, COLUMNS + 2, "A - Left")
            self.stdscr.addstr(6, COLUMNS + 2, "S - Down")
            self.stdscr.addstr(7, COLUMNS + 2, "D - Right")
            self.stdscr.addstr(8, COLUMNS + 2, "Q - Quit")
            self.stdscr.addstr(10, COLUMNS + 2, "Next:")
        else:
            self.stdscr.addstr(0, COLUMNS + 2, f"Счет: {self.score}")
            self.stdscr.addstr(1, COLUMNS + 2, f"Уровень: {self.level}")
            self.stdscr.addstr(3, COLUMNS + 2, "Управление:")
            self.stdscr.addstr(4, COLUMNS + 2, "W - Поворот")
            self.stdscr.addstr(5, COLUMNS + 2, "A - Влево")
            self.stdscr.addstr(6, COLUMNS + 2, "S - Вниз")
            self.stdscr.addstr(7, COLUMNS + 2, "D - Вправо")
            self.stdscr.addstr(8, COLUMNS + 2, "Q - Выход")
            self.stdscr.addstr(10, COLUMNS + 2, "Следующая:")

    def draw_next_piece(self):
        shape = self.next_piece["shape"]
        color = self.next_piece["color"]
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    self.stdscr.addch(y + 12, COLUMNS + 2 + x, '#', curses.color_pair(color))

    def run(self):
        while not self.game_over:
            self.stdscr.clear()
            self.draw_grid()
            self.draw_piece(self.current_piece)
            self.draw_info()
            self.draw_next_piece()
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key == ord('a'):
                self.move_piece(-1, 0)
            elif key == ord('d'):
                self.move_piece(1, 0)
            elif key == ord('s'):
                self.move_piece(0, 1)
            elif key == ord('w'):
                self.rotate_piece()
            elif key == ord('q'):
                break

            self.move_piece(0, 1)

            time.sleep(0.1)

        if self.language == 'en':
            self.stdscr.addstr(ROWS // 2, COLUMNS // 2 - 5, "GAME OVER")
        else:
            self.stdscr.addstr(ROWS // 2, COLUMNS // 2 - 5, "ИГРА ОКОНЧЕНА")
        self.stdscr.refresh()
        time.sleep(2)

def main(stdscr):
    
    language = 'en'  # или 'ru'
    game = Tetris(stdscr, language)
    game.run()

if __name__ == "__main__":
    curses.wrapper(main)
