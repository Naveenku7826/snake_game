import tkinter as tk
import random


CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
INITIAL_SPEED = 180  # Start slower
MIN_SPEED = 60      # Fastest speed
SPEED_STEP = 5      # Speed up by 5ms per food

COLORS = {
    'bg': '#232946',
    'snake': '#eebbc3',
    'food': "#871614",
    'head': '#f6c177',
    'tail': '#b8c1ec',
    'obstacle': '#393e46',
}

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title('Modern Snake Game')
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=GRID_WIDTH*CELL_SIZE, height=GRID_HEIGHT*CELL_SIZE, bg=COLORS['bg'], highlightthickness=0)
        self.canvas.pack()
        self.score = 0
        self.lives = 3
        self.direction = 'Right'
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.food = None
        self.running = True
        self.speed = INITIAL_SPEED
        self.obstacles = []
        self.generate_obstacles()
        self.spawn_food()
        self.draw_snake()
        self.draw_food()
        self.draw_obstacles()
        self.root.bind('<Key>', self.change_direction)
        self.score_label = tk.Label(root, text=f"Score: {self.score}", font=("Segoe UI", 16, "bold"), bg=COLORS['bg'], fg=COLORS['food'])
        self.score_label.pack(fill='x')
        self.lives_label = tk.Label(root, text=self.get_lives_text(), font=("Segoe UI", 14, "bold"), bg=COLORS['bg'], fg='#f6c177')
        self.lives_label.pack(fill='x')
        self.update()

    def generate_obstacles(self):
        self.obstacles = []
        num_obstacles = 10
        for _ in range(num_obstacles):
            while True:
                x = random.randint(2, GRID_WIDTH-3)
                y = random.randint(2, GRID_HEIGHT-3)
                if (x, y) not in self.snake and (x, y) != (5, 5):
                    self.obstacles.append((x, y))
                    break

    def get_lives_text(self):
        return f"Lives: {'❤ '*self.lives}".strip()


    # draw_grid removed for smooth look

    def draw_snake(self):
        self.canvas.delete('snake')
        n = len(self.snake)
        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                # Head: larger, yellow
                self.canvas.create_oval(x*CELL_SIZE, y*CELL_SIZE, (x+1)*CELL_SIZE, (y+1)*CELL_SIZE, fill=COLORS['head'], outline='', tags='snake')
            elif i == n-1:
                # Tail: smaller, blue
                self.canvas.create_oval(x*CELL_SIZE+6, y*CELL_SIZE+6, (x+1)*CELL_SIZE-6, (y+1)*CELL_SIZE-6, fill=COLORS['tail'], outline='', tags='snake')
            else:
                # Body: pink
                self.canvas.create_oval(x*CELL_SIZE+2, y*CELL_SIZE+2, (x+1)*CELL_SIZE-2, (y+1)*CELL_SIZE-2, fill=COLORS['snake'], outline='', tags='snake')

    def draw_obstacles(self):
        self.canvas.delete('obstacle')
        for (x, y) in self.obstacles:
            self.canvas.create_rectangle(x*CELL_SIZE+4, y*CELL_SIZE+4, (x+1)*CELL_SIZE-4, (y+1)*CELL_SIZE-4, fill=COLORS['obstacle'], outline='', tags='obstacle')

    def draw_food(self):
        self.canvas.delete('food')
        x, y = self.food
        # Draw food as a slightly larger, smooth circle
        self.canvas.create_oval(x*CELL_SIZE+4, y*CELL_SIZE+4, (x+1)*CELL_SIZE-4, (y+1)*CELL_SIZE-4, fill=COLORS['food'], outline='', tags='food')

    def spawn_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH-1)
            y = random.randint(0, GRID_HEIGHT-1)
            if (x, y) not in self.snake and (x, y) not in self.obstacles:
                self.food = (x, y)
                break

    def change_direction(self, event):
        key = event.keysym
        opposites = {'Up':'Down', 'Down':'Up', 'Left':'Right', 'Right':'Left'}
        if key in ['Up', 'Down', 'Left', 'Right'] and opposites.get(key) != self.direction:
            self.direction = key

    def update(self):
        if not self.running:
            return
        head_x, head_y = self.snake[0]
        move = {'Up': (0, -1), 'Down': (0, 1), 'Left': (-1, 0), 'Right': (1, 0)}
        dx, dy = move[self.direction]
        new_head = (head_x + dx, head_y + dy)
        # Check collisions
        if (
            new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
            new_head in self.snake or
            new_head in self.obstacles
        ):
            self.lose_life()
            return
        self.snake = [new_head] + self.snake
        score_before = self.score
        if new_head == self.food:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            # Increase speed, but not below MIN_SPEED
            self.speed = max(MIN_SPEED, self.speed - SPEED_STEP)
            self.spawn_food()
            self.draw_food()
            # Move obstacles every 5 points
            if self.score % 5 == 0:
                self.generate_obstacles()
        else:
            self.snake.pop()
        self.draw_snake()
        self.draw_obstacles()
        self.root.after(self.speed, self.update)

    def lose_life(self):
        self.lives -= 1
        self.lives_label.config(text=self.get_lives_text())
        if self.lives > 0:
            self.canvas.create_text(
                GRID_WIDTH*CELL_SIZE//2, GRID_HEIGHT*CELL_SIZE//2,
                text=f"Life lost! {self.lives} left",
                fill='#f6c177', font=("Segoe UI", 22, "bold"), tags='life_lost'
            )
            self.root.after(1200, self.reset_after_life)
        else:
            self.game_over()

    def reset_after_life(self):
        self.canvas.delete('snake')
        self.canvas.delete('food')
        self.canvas.delete('life_lost')
        self.canvas.delete('obstacle')
        self.direction = 'Right'
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.generate_obstacles()
        self.spawn_food()
        self.draw_food()
        self.draw_snake()
        self.draw_obstacles()
        self.running = True
        self.update()

    def game_over(self):
        self.running = False
        self.canvas.create_text(
            GRID_WIDTH*CELL_SIZE//2, GRID_HEIGHT*CELL_SIZE//2,
            text=f"Game Over!\nScore: {self.score}",
            fill=COLORS['food'], font=("Segoe UI", 24, "bold"), tags='gameover'
        )
        self.root.after(2500, self.reset)

    def reset(self):
        self.canvas.delete('snake')
        self.canvas.delete('food')
        self.canvas.delete('gameover')
        self.canvas.delete('obstacle')
        self.score = 0
        self.lives = 3
        self.speed = INITIAL_SPEED
        self.direction = 'Right'
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.generate_obstacles()
        self.score_label.config(text=f"Score: {self.score}")
        self.lives_label.config(text=self.get_lives_text())
        self.spawn_food()
        self.draw_food()
        self.draw_snake()
        self.draw_obstacles()
        self.running = True
        self.update()

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
