import pygame
import random
import math

pygame.init()
win = pygame.display.set_mode((600, 700))
pygame.display.set_caption("PyShooter")
clock = pygame.time.Clock()
run = True

player_balls = []
balls = []
colors = [(255,0,0), (0,255,0), (0,0,255)]
temp = []

score = 0
moves = 40
restart_btn = pygame.Rect(200, 400, 150, 75)

game_state = 2

# 0->Start_Menu, 1->GameOver_Menu, 2->In_Game

class Ball():
    def __init__(self, x, y, color, Type):
        self.x = x
        self.y = y
        self.color = color
        self.x_vel = 0
        self.y_vel = 0
        self.Type = Type
        
    def draw(self):
        pygame.draw.circle(win, self.color, (self.x, self.y), 20)
    
    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel
        
    def shoot(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        print(mouse_x, mouse_y)
        if mouse_y <= 600:
            dx = mouse_x - 300
            dy = 600 - mouse_y
            try:
                angle = math.atan(dx/dy)
                x_vel = 5 * math.sin(angle)
                y_vel = 5 * math.cos(angle)
                print(angle, x_vel, y_vel)
                self.x_vel, self.y_vel = x_vel, (y_vel)*-1
            except:
                print("error")
                
                
                
def startGame():
    global player_balls, balls, score, moves, temp
    player_balls = []
    temp = []
    score, moves = 0, 40
    player_balls.append(Ball(300, 600, colors[random.randrange(0,3)], 0))
    player_balls.append(Ball(300, 600, colors[random.randrange(0,3)], 0))
    balls = []
    for i in range(20, 620, 40):
        for j in range(20, 300, 40):
            balls.append(Ball(i, j, colors[random.randrange(0, 3)], 0))
        
        
def drawBoard():
    global player_balls
    global balls
    player_balls[0].draw()
    pygame.draw.circle(win, player_balls[1].color, (300, 650), 20)
    for ball in balls:
        ball.draw()
    
def movePlayer():
    global player_balls
    global balls
    global temp
    global score
    player_balls[0].move()
    
    if (player_balls[0].x <= 20) or (player_balls[0].x >= 580):
        player_balls[0].x_vel = player_balls[0].x_vel * -1
    if (player_balls[0].y <= 20):
        player_balls[0].x_vel = 0
        player_balls[0].y_vel = 0
        balls.append(player_balls[0])
        player_balls.remove(player_balls[0])
        player_balls.append(Ball(300, 600, colors[random.randrange(0, 3)], 0))
    
    for ball in balls:
        dx = player_balls[0].x - ball.x
        dy = player_balls[0].y - ball.y
        hypot = math.sqrt(dx*dx + dy*dy)
        if hypot < 40:
            player_balls[0].x_vel = 0
            player_balls[0].y_vel = 0
            balls.append(player_balls[0])
            removeBalls(player_balls[0])
            score += len(temp) * 5 + int(len(temp)*len(temp)/5)
            print(score)
            if len(temp) >= 3:
                for l in temp:
                    try:
                        balls.remove(l)
                    except:
                        pass
            temp = []
            player_balls.remove(player_balls[0])
            player_balls.append(Ball(300, 600, colors[random.randrange(0, 3)], 0))
            remove()
            break
        
        
def removeBalls(Ball):
    global balls
    global temp
    for ball in balls:
        dx = Ball.x - ball.x
        dy = Ball.y - ball.y
        hypot = math.sqrt(dx * dx + dy * dy)
        
        if hypot != 0:
            if hypot < 50 and ball.color == Ball.color:
                k = False
                for i in temp:
                    if i == ball:
                        k = True
                        break
                if not k:
                    temp.append(ball)
                    removeBalls(ball)
                    
def remove():
    global balls
    List = []
    for b in balls:
        List.append([b,0])
        
    def func(ball):
        for j in List:
            if j[1] == 0:
                dx = ball.x - j[0].x
                dy = ball.y - j[0].y
                hypot = math.sqrt(dx*dx + dy*dy)
                if hypot != 0 and hypot <= 50:
                    j[1] = 1
                    func(j[0])
    
    for i in List:
        if i[1] == 0:
            bx, by = i[0].x, i[0].y
            in_edge = (bx <= 25 or bx >= 570) or (by <= 25 or by >= 570)
            if in_edge:
                i[1] = 1
                func(i[0])
    for k in List:
        if k[1] == 0:
            if k[0].Type == 0:
                balls.remove(k[0])
                

def drawUI():
    global moves, score
    pygame.draw.line(win, (255, 255, 255), (300, 600), pygame.mouse.get_pos())
    x, y = pygame.mouse.get_pos()
    pygame.draw.line(win, (255, 255, 255), (320, 600), (x+20, y))
    pygame.draw.line(win, (255, 255, 255), (280, 600), (x-20, y))
    main_font = pygame.font.SysFont("comicsans", 50)
    win.blit(main_font.render(f"Moves: {moves}", 1, (255,255,255)), (50, 625))
    win.blit(main_font.render(f"Score: {score}", 1, (255,255,255)), (320, 625))
    
def game():
    global balls, moves, game_state
    for ball in balls:
        ball.move()
        if (ball.x <= 20) or (ball.x >= 580):
            ball.x_vel = ball.x_vel * -1
    if len(balls) == 0:
        game_state = 1
    if moves <= -1:
        game_state = 1
    for ball in balls:
        if ball.y >= 440:
            game_state = 1
            break

startGame()
while run:
    clock.tick(60)
    if game_state == 2:
        win.fill((0,0,0))
        pygame.draw.line(win, (255,255,255), (0, 600), (600, 600))
        drawBoard()
        movePlayer()
        drawUI()
        game()
        pygame.display.update()
        
    if game_state == 1:
        win.fill((0,0,0))
        main_font = pygame.font.SysFont("comicsans", 50)
        score_label = main_font.render(f"Score: {score}", 1, (255,255,255))
        l1_label = main_font.render("GameOver!!!", 1, (255,0,0))
        win.blit(score_label, (230,200))
        win.blit(l1_label, (200,100))
        win.blit(main_font.render("Restart", 1, (0,0,255)), (235, 400))
        pygame.display.update()
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == 2:
                if player_balls[0].x_vel == 0 and player_balls[0].y_vel == 0:
                    player_balls[0].shoot()
                    moves -= 1
            if game_state == 1:
                if restart_btn.collidepoint(pygame.mouse.get_pos()):
                    game_state = 2
                    startGame()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == 2:
                    player_balls[0], player_balls[1] = player_balls[1], player_balls[0]
