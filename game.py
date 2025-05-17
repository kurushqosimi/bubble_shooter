import cv2
import numpy as np
import random
import math
from collections import deque
from dataclasses import dataclass

WIDTH, HEIGHT = 600, 700
GRID_COLS, GRID_ROWS = 15, 12    
GRID_ORIGIN_X, GRID_ORIGIN_Y = 20, 20
GRID_STEP = 40
BALL_R = 20
PLAY_Y = 600                   
FPS = 60

COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

BALL_IMAGES = {
    (255, 0, 0): cv2.imread("assets/red.png", cv2.IMREAD_UNCHANGED),
    (0, 255, 0): cv2.imread("assets/green.png", cv2.IMREAD_UNCHANGED),
    (0, 0, 255): cv2.imread("assets/blue.png", cv2.IMREAD_UNCHANGED),
}

GROUP_BASE_SCORE = 10
GROUP_BONUS_PER_EXTRA = 20
ORPHAN_SCORE = 5

PROJECTILE_SPEED = 9


def clamp(v: int | float, lo: int | float, hi: int | float):
    return max(lo, min(hi, v))


def neighbors4(gx: int, gy: int):
    """4-connected neighbourhood (grid-wise)."""
    return (
        (gx + 1, gy),
        (gx - 1, gy),
        (gx, gy + 1),
        (gx, gy - 1),
    )


def neighbors8(gx: int, gy: int):
    """8-connected neighbourhood (used for collision grouping)."""
    return (
        (gx + 1, gy), (gx - 1, gy), (gx, gy + 1), (gx, gy - 1),
        (gx + 1, gy + 1), (gx - 1, gy + 1), (gx + 1, gy - 1), (gx - 1, gy - 1)
    )


def grid_to_pixel(gx: int, gy: int):
    return GRID_ORIGIN_X + gx * GRID_STEP, GRID_ORIGIN_Y + gy * GRID_STEP


@dataclass
class Ball:
    x: float
    y: float
    color: tuple[int, int, int]
    vx: float = 0.0
    vy: float = 0.0
    moving: bool = True

    def update(self):
        if not self.moving:
            return
        self.x += self.vx
        self.y += self.vy
        if self.x <= BALL_R or self.x >= WIDTH - BALL_R:
            self.vx *= -1
            self.x = clamp(self.x, BALL_R, WIDTH - BALL_R)

    def draw(self, frame):
        img = BALL_IMAGES.get(self.color)
        if img is None:
            return

        h, w = img.shape[:2]
        x, y = int(self.x - w / 2), int(self.y - h / 2)

        if img.shape[2] == 4:
        # Альфа-наложение
            overlay_image_alpha(frame, img[:, :, :3], (x, y), img[:, :, 3])
        else:
            frame[y:y + h, x:x + w] = img


    def grid_pos(self):
        gx = int(round((self.x - GRID_ORIGIN_X) / GRID_STEP))
        gy = int(round((self.y - GRID_ORIGIN_Y) / GRID_STEP))
        return gx, gy

def overlay_image_alpha(img, img_overlay, pos, alpha_mask):
    x, y = pos
    h, w = img_overlay.shape[:2]

    if x < 0 or y < 0 or x + w > img.shape[1] or y + h > img.shape[0]:
        return  # Skip out-of-bounds

    roi = img[y:y + h, x:x + w]

    alpha = alpha_mask / 255.0
    for c in range(3):
        roi[:, :, c] = roi[:, :, c] * (1.0 - alpha) + img_overlay[:, :, c] * alpha

class Game:
    def __init__(self):
        self.reset()

    def aim(self, mx: int, my: int):
        self.aim_x, self.aim_y = mx, my

    def launch_and_shoot(self):
        """Creates the player ball and immediately assigns its velocity."""
        if self.state != "play" or self.player_ball is not None or self.moves == 0:
            return
        self.player_ball = Ball(WIDTH // 2, PLAY_Y, self.next_ball_color, moving=True)
        self.next_ball_color = random.choice(COLORS)

        dx, dy = self.aim_x - WIDTH // 2, self.aim_y - PLAY_Y
        length = math.hypot(dx, dy)
        if length < 1e-6:

            dx, dy = 0, -1
            length = 1
        self.player_ball.vx = PROJECTILE_SPEED * dx / length
        self.player_ball.vy = PROJECTILE_SPEED * dy / length

    def reset(self):
        self.grid: dict[tuple[int, int], Ball] = {}
  
        for gx in range(GRID_COLS):
            for gy in range(7):
                px, py = grid_to_pixel(gx, gy)
                self.grid[(gx, gy)] = Ball(px, py, random.choice(COLORS), moving=False)
        self.player_ball: Ball | None = None
        self.next_ball_color = random.choice(COLORS)
        self.moves = 40
        self.score = 0
        self.state = "play" 
        self.aim_x, self.aim_y = WIDTH // 2, PLAY_Y - 100

    def update(self):
        if self.state != "play":
            return

        if self.player_ball is not None:
            self.player_ball.update()
          
            if self.player_ball.y <= BALL_R:
                self._stick_player()
            else:
               
                for b in self.grid.values():
                    if (self.player_ball.x - b.x) ** 2 + (self.player_ball.y - b.y) ** 2 <= (2 * BALL_R) ** 2:
                        self._stick_player()
                        break

    
        if not self.grid:
            self.state = "win"
        elif self.moves == 0 and self.player_ball is None:
            self.state = "over"

    def draw(self, frame):
        for b in self.grid.values():
            b.draw(frame)
        if self.player_ball is not None:
            self.player_ball.draw(frame)
        cv2.circle(frame, (WIDTH // 2, PLAY_Y + 50), BALL_R, self.next_ball_color, -1)
        cv2.line(frame, (WIDTH // 2, PLAY_Y), (self.aim_x, self.aim_y), (200, 200, 200), 1) # изменение состояния игры. 
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"Score: {self.score}", (20, 645), font, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"Moves: {self.moves}", (320, 645), font, 0.8, (255, 255, 255), 2)
        if self.state == "win":
            cv2.putText(frame, "YOU WIN!", (200, 300), font, 1.2, (0, 255, 0), 3)
            cv2.putText(frame, "Press ENTER to play again", (90, 350), font, 0.8, (0, 255, 0), 2)
        elif self.state == "over":
            cv2.putText(frame, "GAME OVER", (190, 300), font, 1.2, (0, 0, 255), 3)
            cv2.putText(frame, "Press ENTER to restart", (100, 350), font, 0.8, (0, 0, 255), 2)

    def _stick_player(self):
        """Snap the projectile onto the grid and resolve the board state."""
        if self.player_ball is None:
            return
        gx, gy = self.player_ball.grid_pos()
        gx = clamp(gx, 0, GRID_COLS - 1)
        gy = clamp(gy, 0, GRID_ROWS - 1)

        if (gx, gy) in self.grid:
            search_queue = deque([(gx, gy, 0)])
            visited = {(gx, gy)}
            while search_queue:
                x, y, dist = search_queue.popleft()
                for nx, ny in neighbors4(x, y):
                    if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS and (nx, ny) not in visited:
                        if (nx, ny) not in self.grid:
                            gx, gy = nx, ny
                            search_queue.clear()
                            break
                        visited.add((nx, ny))
                        search_queue.append((nx, ny, dist + 1))

        self.player_ball.x, self.player_ball.y = grid_to_pixel(gx, gy)
        self.player_ball.vx = self.player_ball.vy = 0.0
        self.player_ball.moving = False
        self.grid[(gx, gy)] = self.player_ball
        self.player_ball = None
        self.moves -= 1

        self._resolve_matches((gx, gy))

    def _resolve_matches(self, start: tuple[int, int]):
        color = self.grid[start].color
        group = self._collect_same_color(start, color)
        if len(group) >= 3:
            for pos in group:
                self.grid.pop(pos, None)
            
            self.score += GROUP_BASE_SCORE * len(group)
            if len(group) > 3:
                self.score += GROUP_BONUS_PER_EXTRA * (len(group) - 3)
            
            orphan_count = self._drop_orphans()
            self.score += orphan_count * ORPHAN_SCORE

    def _collect_same_color(self, start: tuple[int, int], color):
        visited = set()
        dq = deque([start])
        result = []
        while dq:
            pos = dq.popleft()
            if pos in visited:
                continue
            visited.add(pos)
            b = self.grid.get(pos)
            if b is None or b.color != color:
                continue
            result.append(pos)
            for n in neighbors4(*pos):
                if 0 <= n[0] < GRID_COLS and 0 <= n[1] < GRID_ROWS:
                    dq.append(n)
        return result

    def _drop_orphans(self):
        """Remove balls not connected to the ceiling (row 0). Returns count."""
        if not self.grid:
            return 0
        connected = set()
        dq = deque([p for p in self.grid if p[1] == 0])
        while dq:
            pos = dq.popleft()
            if pos in connected:
                continue
            connected.add(pos)
            for n in neighbors4(*pos):
                if n in self.grid and n not in connected:
                    dq.append(n)
       
        orphan_positions = [p for p in self.grid if p not in connected]
        for p in orphan_positions:
            self.grid.pop(p, None)
        return len(orphan_positions)



def main():
    background = cv2.imread("assets/background.jpg")
    background = cv2.resize(background, (WIDTH, HEIGHT)) 

    game = Game()
    cv2.namedWindow("PyShooter")

    def mouse(event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            game.aim(x, y)
        elif event == cv2.EVENT_LBUTTONDOWN:
            game.aim(x, y)
            game.launch_and_shoot()

    cv2.setMouseCallback("PyShooter", mouse)

    delay_ms = int(1000 / FPS)
    while True:
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        frame[:] = background 
        game.update()
        game.draw(frame)
        cv2.imshow("PyShooter", frame)

        key = cv2.waitKey(delay_ms) & 0xFF
        if key == 27:  # ESC
            break
        elif key == 13 and game.state in ("win", "over"): 
            game.reset() 

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
