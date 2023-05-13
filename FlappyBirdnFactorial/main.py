import pygame as pg
from setting import *
from pygame.locals import *
import random

pg.init()
pg.mixer.init()  # init mixer to use audio

# setup the screen with caption
screen = pg.display.set_mode((WINDOW_W, WINDOW_H))
pg.display.set_caption("Flappy Bird for nFactorial")

# initialize images
image1 = pg.image.load("sprites/background-day.png")
image2 = pg.image.load("sprites/base.png")

clock = pg.time.Clock()

# initialize three birds to choose
red_bird_img = pg.image.load("sprites/redbird-midflap.png")
yellow_bird_img = pg.image.load("sprites/yellowbird-midflap.png")
blue_bird_img = pg.image.load("sprites/bluebird-midflap.png")

# initialize speed of scrolling
scroll_ground = 0
scroll_speed = 4

back = pg.transform.scale(image1, (screen.get_width(), 500))  # background image
ground = pg.transform.scale(image2, (screen.get_width(), 100))  # ground image

game_started = False
game_over = False

# initialize required variables for pipe movement
pipe_gap = 150
pipe_freq = 2000
last_pipe = pg.time.get_ticks() - pipe_freq

points = 0
passed_pipe = False
play_once = 0
record = 0
font = pg.font.Font(None, 30)


# reset game
def reset():
    group_pipe.empty()
    bird.rect.x = 100
    bird.rect.y = int(WINDOW_H / 2)
    new_score = 0
    return new_score


# choose one of three birds depend on the color
def choose_bird_color():
    chosen_bird = None

    while not chosen_bird:
        choose_back = pg.image.load("sprites/choose_back.png")
        screen.blit(choose_back, (0, 0))

        # Display "Choose Your Bird" text
        text = font.render("Choose Your Bird", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WINDOW_W // 2, 50))
        screen.blit(text, text_rect)

        # Calculate positions for the bird images
        bird_y = WINDOW_H // 2 - red_bird_img.get_height() // 2
        bird_spacing = 50
        bird_x_start = WINDOW_W // 2 - (
                red_bird_img.get_width() + yellow_bird_img.get_width() + blue_bird_img.get_width() + 2 * bird_spacing) // 2
        red_bird_x = bird_x_start
        yellow_bird_x = red_bird_x + red_bird_img.get_width() + bird_spacing
        blue_bird_x = yellow_bird_x + yellow_bird_img.get_width() + bird_spacing

        # Display bird images
        screen.blit(red_bird_img, (red_bird_x, bird_y))
        screen.blit(yellow_bird_img, (yellow_bird_x, bird_y))
        screen.blit(blue_bird_img, (blue_bird_x, bird_y))

        # Update the display
        pg.display.flip()

        # Wait for user input
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()
                if red_bird_img.get_rect(x=red_bird_x, y=bird_y).collidepoint(mouse_pos):
                    return "redbird"
                elif yellow_bird_img.get_rect(x=yellow_bird_x, y=bird_y).collidepoint(mouse_pos):
                    return "yellowbird"
                elif blue_bird_img.get_rect(x=blue_bird_x, y=bird_y).collidepoint(mouse_pos):
                    return "bluebird"

            if event.type == pg.QUIT:
                pg.quit()
                return


choosen_bird = choose_bird_color()

score_images = [pg.image.load(f"sprites/{i}.png") for i in range(10)]


# function to display score on the screen
def display_score(score, screen):
    record_text = font.render(f"Record: {record}", True, (255, 255, 255))
    record_rect = record_text.get_rect(center=(WINDOW_W // 2, WINDOW_H - 30))
    screen.blit(record_text, record_rect)
    score_str = str(score)
    score_digits = [int(digit) for digit in score_str]

    # Calculate the total width of the score images
    total_width = sum(score_images[digit].get_width() for digit in score_digits)

    # Calculate the x-coordinate to center the score
    x = (screen.get_width() - total_width) // 2

    # Blit each digit of the score onto the screen
    for digit in score_digits:
        digit_image = score_images[digit]
        screen.blit(digit_image, (x, 10))
        x += digit_image.get_width()


# ------------------------Bird Class-------------------------------------
class MyBird(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)

        self.current_frame = 0
        self.birds = [f"sprites/{choosen_bird}-upflap.png", f"sprites/{choosen_bird}-midflap.png",
                      f"sprites/{choosen_bird}-downflap.png"]
        self.frame_delay = 10
        self.delay_counter = 0

        self.image = pg.image.load(f"sprites/{choosen_bird}-midflap.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

        self.velocity = 0
        self.space_held = False

    def update(self):
        # show welcome screen
        if not game_started and not game_over:
            welcome_image = pg.image.load("sprites/message.png")
            screen.blit(welcome_image, (WINDOW_W // 2 - welcome_image.get_width() // 2,
                                        WINDOW_H // 2 - welcome_image.get_height() // 2))

        # if mouse is clicked and game started
        if game_started:
            # creating gravity for the bird
            self.velocity += 0.5
            if self.velocity > 8:
                self.velocity = 8
            if self.rect.bottom < 485:
                self.rect.y += int(self.velocity)
        if not game_over:
            # jumping - using space keyboard
            keys = pg.key.get_pressed()
            if keys[K_SPACE] and not self.space_held:
                wing_sound = pg.mixer.Sound("audio/wing.wav")
                wing_sound.play()
                self.velocity = - 9
            self.space_held = keys[K_SPACE]

            # bird animation
            if self.delay_counter >= self.frame_delay:
                # Update the bird's image
                bird.image = pg.image.load(self.birds[self.current_frame])
                # rotate the bird
                self.image = pg.transform.rotate(bird.image, self.velocity * -2)
                self.current_frame = (self.current_frame + 1) % len(self.birds)

                self.delay_counter = 0
            else:
                self.delay_counter += 1
        else:
            # if game over show the "game over" image and stop the screen
            self.image = pg.transform.rotate(bird.image, -90)
            game_over_image = pg.image.load("sprites/gameover.png")
            screen.blit(game_over_image, (WINDOW_W // 2 - game_over_image.get_width() // 2,
                                          WINDOW_H // 2 - game_over_image.get_height() // 2))


# ------------------------Pipe Class-------------------------------------
class Pipe(pg.sprite.Sprite):
    def __init__(self, x, y, position):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("sprites/pipe-red.png")
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pg.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        else:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    # movement of pipes
    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


# ------------------------Button Class-------------------------------------
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]

    def draw(self):
        action = False
        # get mouse position
        pos = pg.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pg.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action


# creating two groups of two classes
group_bird = pg.sprite.Group()
group_pipe = pg.sprite.Group()

# create our one bird
bird = MyBird(100, int(WINDOW_H / 2))
group_bird.add(bird)

# create restart button
restart_img = pg.image.load("sprites/reset.png")
restart_img = pg.transform.scale(restart_img, (100, 30))
restart = Button(WINDOW_W // 2 - 50, WINDOW_H // 2 - 100, restart_img)

while True:
    clock.tick(FRAME_R)
    # draw background
    screen.blit(back, (0, 0))

    group_bird.draw(screen)
    group_bird.update()

    group_pipe.draw(screen)
    # draw the ground
    screen.blit(ground, (scroll_ground, 500))

    # check the points
    if len(group_pipe) > 0:
        if group_bird.sprites()[0].rect.left > group_pipe.sprites()[0].rect.left \
                and group_bird.sprites()[0].rect.right < group_pipe.sprites()[0].rect.right \
                and not passed_pipe:
            passed_pipe = True
        if passed_pipe:
            if group_bird.sprites()[0].rect.left > group_pipe.sprites()[0].rect.right:
                points += 1
                point_sound = pg.mixer.Sound("audio/point.wav")
                point_sound.play()
                passed_pipe = False

    display_score(points, screen)
    # check if bird touched the pipe or flew over the top of the screen
    if pg.sprite.groupcollide(group_bird, group_pipe, False, False) or bird.rect.top < 0:
        if play_once == 0:
            hit_sound = pg.mixer.Sound("audio/hit.wav")
            hit_sound.play()
            die_sound = pg.mixer.Sound("audio/die.wav")
            die_sound.play()
        play_once += 1
        game_over = True

    # check if bird at the bottom
    if bird.rect.bottom > 480:
        if play_once == 0:
            die_sound = pg.mixer.Sound("audio/die.wav")
            die_sound.play()
        play_once += 1
        game_over = True
        game_started = False

    # START THE GAME
    if not game_over and game_started:
        pipe_height = random.randint(-100, 100)
        # generate new pipes
        curr_time = pg.time.get_ticks()
        if curr_time - last_pipe > pipe_freq:
            btm_pipe = Pipe(WINDOW_W, int(WINDOW_H / 2) + pipe_height, -1)
            group_pipe.add(btm_pipe)
            top_pipe = Pipe(WINDOW_W, int(WINDOW_H / 2) + pipe_height, 1)
            group_pipe.add(top_pipe)
            last_pipe = curr_time

        # ground movement effect
        scroll_ground -= scroll_speed
        if abs(scroll_ground) > 50:
            scroll_ground = 0

        group_pipe.update()

    # if lost, ask for restart and set record
    if game_over:
        if restart.draw():
            game_over = False
            if points > record:
                record = points
            points = reset()

    for e in pg.event.get():
        if e.type == pg.QUIT:
            break
        if e.type == pg.MOUSEBUTTONDOWN and game_started == False and game_over == False:
            game_started = True

    pg.display.update()

pg.quit()