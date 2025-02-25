import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 30
GRID_WIDTH = 20
GRID_HEIGHT = 20
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE
SNAKE_SPEED = 15

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
CYAN = (50, 255, 255)

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]]   # J
]

class Tetnake:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetnake")
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT - 2)]  # Start near bottom
        self.direction = (0, -1)  # Start moving up
        self.current_piece = self.new_piece()
        self.piece_pos = [GRID_WIDTH // 2 - 1, 0]
        self.food = None
        self.score = 0
        self.game_over = False
        self.spawn_food()
    def new_piece(self):
        shape = random.choice(SHAPES)
        return [row[:] for row in shape]

    def spawn_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake and not self.check_piece_collision(x, y):
                self.food = (x, y)
                break

    def check_piece_collision(self, x, y):
        for i in range(len(self.current_piece)):
            for j in range(len(self.current_piece[0])):
                if self.current_piece[i][j]:
                    new_x = x + j
                    new_y = y + i
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y < GRID_HEIGHT and self.grid[new_y][new_x])):
                        return True
        return False

    def merge_piece(self):
        for i in range(len(self.current_piece)):
            for j in range(len(self.current_piece[0])):
                if self.current_piece[i][j]:
                    x = self.piece_pos[0] + j
                    y = self.piece_pos[1] + i
                    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                        self.grid[y][x] = 1
        self.check_lines()

    def check_lines(self):
        lines_cleared = 0
        for i in range(GRID_HEIGHT - 1, -1, -1):
            if all(self.grid[i]):
                del self.grid[i]
                self.grid.insert(0, [0] * GRID_WIDTH)
                lines_cleared += 1
        self.score += lines_cleared * 100

    def rotate_piece(self):
        self.current_piece = list(zip(*self.current_piece[::-1]))

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen, BLUE, 
                                   (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))

        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            color = GREEN if i == 0 else CYAN  # Head is different color
            pygame.draw.rect(self.screen, color, 
                           (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))

        # Draw current piece
        for i in range(len(self.current_piece)):
            for j in range(len(self.current_piece[0])):
                if self.current_piece[i][j]:
                    x = self.piece_pos[0] + j
                    y = self.piece_pos[1] + i
                    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                        pygame.draw.rect(self.screen, YELLOW, 
                                      (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))

        # Draw food
        if self.food:
            pygame.draw.rect(self.screen, RED, 
                           (self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

    def run(self):
        piece_fall_timer = 0
        while not self.game_over:
            piece_fall_timer += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.direction = (1, 0)
                    elif event.key == pygame.K_UP:
                        self.direction = (0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.direction = (0, 1)
                    elif event.key == pygame.K_SPACE:
                        self.rotate_piece()

            # Move snake
            head_x, head_y = self.snake[0]
            new_head = (head_x + self.direction[0], head_y + self.direction[1])
            
            # Check collisions
            if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or 
                new_head in self.snake[1:]):
                print(f"Snake collision at {new_head}")
                self.game_over = True
                continue

            self.snake.insert(0, new_head)
            
            # Check food
            if new_head == self.food:
                self.score += 50
                self.spawn_food()
            else:
                self.snake.pop()

            # Move piece
            if piece_fall_timer >= 30:  # Fall every 30 frames
                piece_fall_timer = 0
                new_pos = [self.piece_pos[0], self.piece_pos[1] + 1]
                if self.check_piece_collision(new_pos[0], new_pos[1]):
                    self.merge_piece()
                    self.current_piece = self.new_piece()
                    self.piece_pos = [GRID_WIDTH // 2 - 1, 0]
                    if self.check_piece_collision(self.piece_pos[0], self.piece_pos[1]):
                        print(f"Piece collision at spawn: {self.piece_pos}")
                        self.game_over = True
                else:
                    self.piece_pos = new_pos

            self.draw()
            pygame.display.flip()
            self.clock.tick(SNAKE_SPEED)

        # Game over screen
        print(f"Game Over with score: {self.score}")
        font = pygame.font.Font(None, 48)
        text = font.render(f"Game Over! Score: {self.score}", True, WHITE)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)

if __name__ == "__main__":
    game = Tetnake()
    game.run()
    pygame.quit()